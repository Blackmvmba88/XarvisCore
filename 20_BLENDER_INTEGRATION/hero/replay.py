from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .telemetry_window import TelemetryWindow
from .scheduler import Scheduler, Device, Task, RenderJob


@dataclass
class Assignment:
    ts: datetime
    job_id: str
    task_id: str
    assigned_device_id: Optional[str]
    reason: str


@dataclass
class SimulationResult:
    assignments: List[Assignment]
    deadline_misses: int

    def to_dict(self):
        return {
            'assignments': [
                {
                    'ts': a.ts.isoformat(),
                    'job_id': a.job_id,
                    'task_id': a.task_id,
                    'assigned_device_id': a.assigned_device_id,
                    'reason': a.reason,
                }
                for a in self.assignments
            ],
            'deadline_misses': self.deadline_misses,
        }

class Policy:
    """Base policy interface for simulation."""

    def plan(self, scheduler: Scheduler, pending_jobs: List[RenderJob]) -> List[Dict[str, Any]]:
        raise NotImplementedError()


class GreedyPolicy(Policy):
    """Greedy: respects job order, uses scheduler._find_best_device semantics via a dry_run.
    This delegates to the scheduler.dry_run which implements the current admission/fallback rules.
    """

    def plan(self, scheduler: Scheduler, pending_jobs: List[RenderJob]) -> List[Dict[str, Any]]:
        # submit all pending jobs into a copy of the scheduler queue and dry_run
        # (scheduler.dry_run already sorts by priority)
        # We'll mutate scheduler.queue temporarily
        for job in pending_jobs:
            scheduler.submit(job)
        plan = scheduler.dry_run()
        # cleanup queue to avoid double-submits in caller
        # remove the jobs we added
        scheduler.queue = [q for q in scheduler.queue if q.job_id not in {j.job_id for j in pending_jobs}]
        return plan['plans']


class EDFPolicy(Policy):
    """Simple EDF-like policy for simulation. It orders tasks by deadline (earliest) and
    selects the highest-health device available at the time.

    Note: This is a lightweight skeleton - the full EDF/cost model should live in a
    dedicated module and use runtime estimators.
    """

    def plan(self, scheduler: Scheduler, pending_jobs: List[RenderJob]) -> List[Dict[str, Any]]:
        # flatten tasks with deadline metadata (deadline as datetime stored in job.deadline attr if present)
        tasks_with_meta: List[Tuple[Optional[datetime], RenderJob, Task]] = []
        for job in pending_jobs:
            for t in job.tasks:
                deadline = getattr(job, 'deadline', None)
                tasks_with_meta.append((deadline, job, t))
        # sort by earliest deadline first (None goes last)
        tasks_with_meta.sort(key=lambda x: (x[0] is None, x[0] or datetime.max))

        plans: List[Dict[str, Any]] = []
        # shallow copy of devices to simulate allocations
        sim_devices = [Device(d.id, d.backend, d.total_memory_mb, d.free_memory_mb, d.compute_score) for d in scheduler.devices]

        for deadline, job, task in tasks_with_meta:
            # choose best device among sim_devices (healthy and with memory)
            candidates = [d for d in sim_devices if d.free_memory_mb >= task.required_memory_mb and d.compute_score > 0.0]
            # prefer highest compute_score
            candidates.sort(key=lambda d: d.compute_score, reverse=True)
            assigned = None
            if candidates:
                assigned = candidates[0]
                assigned.allocate(task.required_memory_mb)
                plans.append({'job_id': job.job_id, 'task_id': task.task_id, 'assigned_device_id': assigned.id, 'assigned_backend': assigned.backend, 'frames': task.frames, 'reason': 'assigned_edf'})
                continue
            # cpu fallback
            if task.allow_cpu_fallback:
                cpu_devices = [d for d in sim_devices if d.backend == 'CPU' and d.free_memory_mb >= task.required_memory_mb]
                if cpu_devices:
                    cpu_devices.sort(key=lambda d: d.compute_score, reverse=True)
                    cpu = cpu_devices[0]
                    cpu.allocate(task.required_memory_mb)
                    plans.append({'job_id': job.job_id, 'task_id': task.task_id, 'assigned_device_id': cpu.id, 'assigned_backend': cpu.backend, 'frames': task.frames, 'reason': 'cpu_fallback'})
                    continue
            plans.append({'job_id': job.job_id, 'task_id': task.task_id, 'assigned_device_id': None, 'assigned_backend': None, 'frames': task.frames, 'reason': 'rejected'})

        return plans


class Simulator:
    """Deterministic simulator for traces. The trace is a list of events sorted by 'ts' chronological order.

    Event types:
      - {'type': 'telemetry', 'ts': datetime, 'sample': TelemetrySample-like}
      - {'type': 'job', 'ts': datetime, 'job': RenderJob, 'deadline': Optional[datetime]}

    The Simulator feeds telemetry into a TelemetryWindow, updates Scheduler from the window, and calls
    the policy at job submission times to compute assignments. The simulation is deterministic (events sorted by ts).

    This class also provides trace load/save helpers for JSON files so traces are easy to persist and share.
    """

    def __init__(self, devices: Optional[List[Dict[str, Any]]] = None):
        self.window = TelemetryWindow()
        self.scheduler = Scheduler()
        if devices:
            self.scheduler.register_devices(devices)

    def simulate(self, trace: List[Dict[str, Any]], policy: Policy) -> SimulationResult:
        # sort events by ts to ensure determinism
        trace_sorted = sorted(trace, key=lambda e: e['ts'])
        pending_jobs: List[RenderJob] = []
        assignments: List[Assignment] = []
        deadline_misses = 0

        for ev in trace_sorted:
            ts = ev['ts']
            if ev['type'] == 'telemetry':
                self.window.ingest(ev['sample'], now=ts)
            elif ev['type'] == 'job':
                job: RenderJob = ev['job']
                # attach deadline if present
                if 'deadline' in ev:
                    setattr(job, 'deadline', ev['deadline'])
                pending_jobs.append(job)

            # update scheduler device states from window
            self.scheduler.update_from_window(self.window, now=ts)

            # when there are pending jobs at this timestamp, ask policy to plan
            if any(ev2['ts'] == ts and ev2['type'] == 'job' for ev2 in trace_sorted):
                plan_entries = policy.plan(self.scheduler, pending_jobs)
                # record assignments for all jobs in pending_jobs
                for p in plan_entries:
                    assignments.append(Assignment(ts=ts, job_id=p['job_id'], task_id=p['task_id'], assigned_device_id=p.get('assigned_device_id'), reason=p.get('reason', '')))
                    # simple deadline miss counting: if a job had a deadline and it's rejected -> miss
                    job_deadline = next((j for j in pending_jobs if j.job_id == p['job_id']), None)
                    if p.get('assigned_device_id') is None and getattr(job_deadline, 'deadline', None) is not None:
                        deadline_misses += 1
                # clear pending jobs after planning (we assume single-shot submit semantics)
                pending_jobs = []

        return SimulationResult(assignments=assignments, deadline_misses=deadline_misses)

    # Trace IO helpers -----------------------------------------------------
    @staticmethod
    def _serialize_event(ev: Dict[str, Any]) -> Dict[str, Any]:
        # ts -> ISO
        out = {'type': ev['type'], 'ts': ev['ts'].isoformat()}
        if ev['type'] == 'telemetry':
            s = ev['sample']
            out['sample'] = {
                'ts': s.ts.isoformat(),
                'device_id': s.device_id,
                'gpu_temp': s.gpu_temp,
                'gpu_memory_used_gb': s.gpu_memory_used_gb,
                'gpu_memory_total_gb': s.gpu_memory_total_gb,
                'is_throttling': s.is_throttling,
                'power_watts': s.power_watts,
            }
        elif ev['type'] == 'job':
            job = ev['job']
            job_dict = {
                'job_id': job.job_id,
                'priority': job.priority,
                'tasks': [
                    {
                        'task_id': t.task_id,
                        'required_memory_mb': t.required_memory_mb,
                        'requires_gpu': t.requires_gpu,
                        'frames': t.frames,
                        'priority': t.priority,
                        'allow_cpu_fallback': t.allow_cpu_fallback,
                    }
                    for t in job.tasks
                ],
            }
            out['job'] = job_dict
            if getattr(job, 'deadline', None) is not None:
                out['deadline'] = job.deadline.isoformat()
        return out

    @staticmethod
    def _deserialize_event(ev: Dict[str, Any]):
        from datetime import datetime
        from .telemetry_model import TelemetrySample
        from .scheduler import Task, RenderJob

        t = datetime.fromisoformat(ev['ts'])
        if ev['type'] == 'telemetry':
            s = ev['sample']
            sample = TelemetrySample(ts=datetime.fromisoformat(s['ts']), device_id=s['device_id'], gpu_temp=s['gpu_temp'], gpu_memory_used_gb=s['gpu_memory_used_gb'], gpu_memory_total_gb=s['gpu_memory_total_gb'], is_throttling=s.get('is_throttling', False), power_watts=s.get('power_watts'))
            return {'type': 'telemetry', 'ts': t, 'sample': sample}
        elif ev['type'] == 'job':
            j = ev['job']
            tasks = [Task(task_id=td['task_id'], required_memory_mb=td.get('required_memory_mb', 0), requires_gpu=td.get('requires_gpu', False), frames=td.get('frames', 1), priority=td.get('priority', 0), allow_cpu_fallback=td.get('allow_cpu_fallback', False)) for td in j.get('tasks', [])]
            job = RenderJob(j['job_id'], tasks, priority=j.get('priority', 0))
            if 'deadline' in ev:
                job.deadline = datetime.fromisoformat(ev['deadline'])
            return {'type': 'job', 'ts': t, 'job': job, 'deadline': getattr(job, 'deadline', None)}
        else:
            raise ValueError('unknown event type')

    @staticmethod
    def save_trace_to_file(trace: List[Dict[str, Any]], path: str) -> None:
        import json

        serial = [Simulator._serialize_event(e) for e in trace]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(serial, f, indent=2)

    @staticmethod
    def load_trace_from_file(path: str) -> List[Dict[str, Any]]:
        import json
        from datetime import datetime

        with open(path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        return [Simulator._deserialize_event(e) for e in raw]
