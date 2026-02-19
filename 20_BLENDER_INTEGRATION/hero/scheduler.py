# Scheduler skeleton for Hero Mode (enhanced)
# Provides dry-run planning for device assignment and policy validation.

from __future__ import annotations

from typing import List, Dict, Any, Optional, Tuple


class Device:
    def __init__(
        self,
        id: str,
        backend: str = "CPU",
        total_memory_mb: int = 0,
        free_memory_mb: int = 0,
        compute_score: float = 0.0,
        **extra: Any,
    ):
        self.id = id
        self.backend = backend  # 'CUDA'|'OPTIX'|'METAL'|'CPU'
        self.total_memory_mb = int(total_memory_mb)
        self.free_memory_mb = int(free_memory_mb)
        self.compute_score = float(compute_score)
        # Preserve unknown fields so detection can evolve without breaking register_devices().
        self.extra: Dict[str, Any] = dict(extra or {})

    def allocate(self, mb: int) -> bool:
        if self.free_memory_mb >= mb:
            self.free_memory_mb -= mb
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'id': self.id,
            'backend': self.backend,
            'total_memory_mb': self.total_memory_mb,
            'free_memory_mb': self.free_memory_mb,
            'compute_score': self.compute_score,
        }
        data.update(self.extra)
        return data


class Task:
    def __init__(
        self,
        task_id: str,
        required_memory_mb: int = 0,
        requires_gpu: bool = False,
        frames: int = 1,
        priority: int = 0,
        allow_cpu_fallback: bool = False,
        deadline_ts: Optional[float] = None,
        est_seconds_per_frame: Optional[float] = None,
        **extra: Any,
    ):
        self.task_id = task_id
        self.required_memory_mb = int(required_memory_mb)
        self.requires_gpu = bool(requires_gpu)
        self.frames = int(frames)
        self.priority = int(priority)
        self.allow_cpu_fallback = bool(allow_cpu_fallback)
        self.deadline_ts = float(deadline_ts) if deadline_ts is not None else None
        self.est_seconds_per_frame = float(est_seconds_per_frame) if est_seconds_per_frame is not None else None
        self.extra: Dict[str, Any] = dict(extra or {})

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'task_id': self.task_id,
            'required_memory_mb': self.required_memory_mb,
            'requires_gpu': self.requires_gpu,
            'frames': self.frames,
            'priority': self.priority,
            'allow_cpu_fallback': self.allow_cpu_fallback,
            'deadline_ts': self.deadline_ts,
            'est_seconds_per_frame': self.est_seconds_per_frame,
        }
        data.update(self.extra)
        return data


class RenderJob:
    def __init__(self, job_id: str, tasks: List[Task], priority: int = 0, deadline_ts: Optional[float] = None):
        self.job_id = job_id
        self.tasks = tasks
        self.priority = int(priority)
        self.deadline_ts = float(deadline_ts) if deadline_ts is not None else None
        self._submit_seq: int = 0  # assigned by Scheduler.submit()


class Scheduler:
    """Scheduler supports device registration and dry-run planning.

    Usage:
      s = Scheduler()
      s.add_device(Device(...))
      s.submit(RenderJob(...))
      plan = s.dry_run()
    """

    def __init__(self):
        self.queue: List[RenderJob] = []
        self.devices: List[Device] = []
        self._submit_seq = 0

    def add_device(self, device: Device):
        self.devices.append(device)

    def register_devices(self, devices: List[Dict[str, Any]]):
        self.devices = [Device(**d) for d in devices]

    def submit(self, job: RenderJob):
        self._submit_seq += 1
        job._submit_seq = self._submit_seq
        self.queue.append(job)
        return job.job_id

    def list_devices(self) -> List[Dict[str, Any]]:
        return [d.to_dict() for d in self.devices]

    def _deadline_key(self, job: RenderJob, task: Task) -> Tuple[int, float]:
        # (has_deadline, deadline) so "no deadline" sorts last.
        d = task.deadline_ts if task.deadline_ts is not None else job.deadline_ts
        if d is None:
            return (1, float("inf"))
        return (0, float(d))

    def _score_device(self, task: Task, d: Device) -> float:
        # Best-fit on memory (prefer minimal slack) plus compute score.
        # Normalize to stable-ish 0..1-ish weights.
        slack = float(d.free_memory_mb - task.required_memory_mb)
        total = float(d.total_memory_mb or max(d.free_memory_mb, 1))
        mem_score = 1.0 - max(0.0, min(1.0, slack / max(total, 1.0)))
        compute_score = float(d.compute_score)
        # Favor memory fit first so small tasks don't consume the largest GPUs.
        return (0.65 * mem_score) + (0.35 * compute_score)

    def _find_best_device(self, task: Task, devices: List[Device]) -> Optional[Device]:
        candidates = []
        for d in devices:
            # If GPU is required, never pick CPU here; CPU fallback is handled explicitly below
            # so we can label it as such in the plan.
            if task.requires_gpu and d.backend == 'CPU':
                continue
            if d.free_memory_mb < task.required_memory_mb:
                continue
            score = self._score_device(task, d)
            candidates.append((score, d))
        if not candidates:
            return None
        # pick highest score
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    def dry_run(self) -> Dict[str, Any]:
        """Create an execution plan without changing real devices. Returns plan dict.

        Plan format:
          { 'plans': [ { job_id, task_id, assigned_device_id (or null), reason }, ... ], 'devices': [device dicts after simulated allocation] }
        """
        # copy device state to simulate allocations (preserve extra metadata)
        sim_devices = [
            Device(
                id=d.id,
                backend=d.backend,
                total_memory_mb=d.total_memory_mb,
                free_memory_mb=d.free_memory_mb,
                compute_score=d.compute_score,
                **getattr(d, "extra", {}),
            )
            for d in self.devices
        ]

        # sort jobs by priority desc (higher first), then earliest deadline, then FIFO
        jobs = sorted(
            self.queue,
            key=lambda j: (
                -j.priority,
                (0, j.deadline_ts) if j.deadline_ts is not None else (1, float("inf")),
                j._submit_seq,
            ),
        )

        plans = []
        device_time: Dict[str, float] = {d.id: 0.0 for d in sim_devices}

        for job in jobs:
            # tasks sorted by task.priority desc, then earliest deadline
            tasks = sorted(
                job.tasks,
                key=lambda t: (
                    -t.priority,
                    self._deadline_key(job, t),
                ),
            )
            for task in tasks:
                assigned = self._find_best_device(task, sim_devices)
                if assigned:
                    # simulate allocate
                    ok = assigned.allocate(task.required_memory_mb)
                    if ok:
                        est_spf = task.est_seconds_per_frame if task.est_seconds_per_frame is not None else None
                        # If no per-frame estimate, leave timing fields null.
                        if est_spf is None:
                            start_est = end_est = None
                        else:
                            duration = (float(task.frames) * float(est_spf)) / max(float(assigned.compute_score), 0.01)
                            start_est = device_time.get(assigned.id, 0.0)
                            end_est = start_est + duration
                            device_time[assigned.id] = end_est

                        plans.append(
                            {
                                'job_id': job.job_id,
                                'task_id': task.task_id,
                                'priority': {'job': job.priority, 'task': task.priority},
                                'deadline_ts': task.deadline_ts if task.deadline_ts is not None else job.deadline_ts,
                                'required_memory_mb': task.required_memory_mb,
                                'frames': task.frames,
                                'assigned_device_id': assigned.id,
                                'assigned_backend': assigned.backend,
                                'reason': 'assigned',
                                'score': self._score_device(task, assigned),
                                'start_estimate_s': start_est,
                                'end_estimate_s': end_est,
                            }
                        )
                        continue
                # If no assigned device, check CPU fallback if allowed
                if task.allow_cpu_fallback:
                    cpu_devices = [d for d in sim_devices if d.backend == 'CPU' and d.free_memory_mb >= task.required_memory_mb]
                    if cpu_devices:
                        # pick best CPU by compute_score
                        cpu_devices.sort(key=lambda d: (d.compute_score, d.free_memory_mb), reverse=True)
                        cpu = cpu_devices[0]
                        cpu.allocate(task.required_memory_mb)
                        plans.append(
                            {
                                'job_id': job.job_id,
                                'task_id': task.task_id,
                                'priority': {'job': job.priority, 'task': task.priority},
                                'deadline_ts': task.deadline_ts if task.deadline_ts is not None else job.deadline_ts,
                                'required_memory_mb': task.required_memory_mb,
                                'frames': task.frames,
                                'assigned_device_id': cpu.id,
                                'assigned_backend': cpu.backend,
                                'reason': 'cpu_fallback',
                                'score': self._score_device(task, cpu),
                                'start_estimate_s': None,
                                'end_estimate_s': None,
                            }
                        )
                        continue
                # No assignment possible
                plans.append(
                    {
                        'job_id': job.job_id,
                        'task_id': task.task_id,
                        'priority': {'job': job.priority, 'task': task.priority},
                        'deadline_ts': task.deadline_ts if task.deadline_ts is not None else job.deadline_ts,
                        'required_memory_mb': task.required_memory_mb,
                        'frames': task.frames,
                        'assigned_device_id': None,
                        'assigned_backend': None,
                        'reason': 'rejected',
                        'score': None,
                        'start_estimate_s': None,
                        'end_estimate_s': None,
                    }
                )

        return {'plans': plans, 'devices': [d.to_dict() for d in sim_devices]}

    @staticmethod
    def plan_to_markdown(plan: Dict[str, Any]) -> str:
        """Render a human-readable Markdown table for a plan dict."""
        rows = plan.get("plans") or []
        header = "| job | task | reason | device | backend | mem_mb | frames | job_pri | task_pri | deadline_ts |\n|---|---|---|---|---|---:|---:|---:|---:|---:|"
        out = [header]
        for p in rows:
            pri = p.get("priority") or {}
            out.append(
                "| {job} | {task} | {reason} | {dev} | {backend} | {mem} | {frames} | {jpri} | {tpri} | {dl} |".format(
                    job=p.get("job_id", ""),
                    task=p.get("task_id", ""),
                    reason=p.get("reason", ""),
                    dev=p.get("assigned_device_id", "") or "",
                    backend=p.get("assigned_backend", "") or "",
                    mem=p.get("required_memory_mb", "") or "",
                    frames=p.get("frames", "") or "",
                    jpri=pri.get("job", "") if isinstance(pri, dict) else "",
                    tpri=pri.get("task", "") if isinstance(pri, dict) else "",
                    dl=p.get("deadline_ts", "") or "",
                )
            )
        return "\n".join(out)
