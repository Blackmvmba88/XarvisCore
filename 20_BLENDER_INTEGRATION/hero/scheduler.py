# Scheduler skeleton for Hero Mode (enhanced)
# Provides dry-run planning for device assignment and policy validation.

from typing import List, Dict, Any, Optional


class Device:
    def __init__(self, id: str, backend: str = "CPU", total_memory_mb: int = 0, free_memory_mb: int = 0, compute_score: float = 0.0):
        self.id = id
        self.backend = backend  # 'CUDA'|'OPTIX'|'METAL'|'CPU'
        self.total_memory_mb = int(total_memory_mb)
        self.free_memory_mb = int(free_memory_mb)
        self.compute_score = float(compute_score)

    def allocate(self, mb: int) -> bool:
        if self.free_memory_mb >= mb:
            self.free_memory_mb -= mb
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "backend": self.backend,
            "total_memory_mb": self.total_memory_mb,
            "free_memory_mb": self.free_memory_mb,
            "compute_score": self.compute_score,
        }


class Task:
    def __init__(
        self,
        task_id: str,
        required_memory_mb: int = 0,
        requires_gpu: bool = False,
        frames: int = 1,
        priority: int = 0,
        allow_cpu_fallback: bool = False,
    ):
        self.task_id = task_id
        self.required_memory_mb = int(required_memory_mb)
        self.requires_gpu = bool(requires_gpu)
        self.frames = int(frames)
        self.priority = int(priority)
        self.allow_cpu_fallback = bool(allow_cpu_fallback)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "required_memory_mb": self.required_memory_mb,
            "requires_gpu": self.requires_gpu,
            "frames": self.frames,
            "priority": self.priority,
            "allow_cpu_fallback": self.allow_cpu_fallback,
        }


class RenderJob:
    def __init__(self, job_id: str, tasks: List[Task], priority: int = 0):
        self.job_id = job_id
        self.tasks = tasks
        self.priority = int(priority)


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

    def add_device(self, device: Device):
        self.devices.append(device)

    def register_devices(self, devices: List[Dict[str, Any]]):
        self.devices = [Device(**d) for d in devices]

    def submit(self, job: RenderJob):
        self.queue.append(job)
        return job.job_id

    def _find_best_device(self, task: Task, devices: List[Device]) -> Optional[Device]:
        candidates = []
        for d in devices:
            # If GPU is required, never pick CPU here; CPU fallback is handled explicitly below
            # so we can label it as such in the plan.
            if task.requires_gpu and d.backend == "CPU":
                continue
            if d.free_memory_mb < task.required_memory_mb:
                continue
            candidates.append((d.compute_score, d))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    def dry_run(self) -> Dict[str, Any]:
        """Create an execution plan without changing real devices. Returns plan dict.

        Plan format:
          { 'plans': [ { job_id, task_id, assigned_device_id (or null), reason }, ... ], 'devices': [device dicts after simulated allocation] }
        """
        # copy device state to simulate allocations
        sim_devices = [Device(d.id, d.backend, d.total_memory_mb, d.free_memory_mb, d.compute_score) for d in self.devices]

        # sort jobs by priority desc (higher first), then FIFO
        jobs = sorted(self.queue, key=lambda j: j.priority, reverse=True)

        plans = []
        for job in jobs:
            # tasks sorted by task.priority desc
            tasks = sorted(job.tasks, key=lambda t: t.priority, reverse=True)
            for task in tasks:
                assigned = self._find_best_device(task, sim_devices)
                if assigned:
                    ok = assigned.allocate(task.required_memory_mb)
                    if ok:
                        plans.append(
                            {
                                "job_id": job.job_id,
                                "task_id": task.task_id,
                                "assigned_device_id": assigned.id,
                                "assigned_backend": assigned.backend,
                                "frames": task.frames,
                                "reason": "assigned",
                            }
                        )
                        continue

                if task.allow_cpu_fallback:
                    cpu_devices = [d for d in sim_devices if d.backend == "CPU" and d.free_memory_mb >= task.required_memory_mb]
                    if cpu_devices:
                        cpu_devices.sort(key=lambda d: d.compute_score, reverse=True)
                        cpu = cpu_devices[0]
                        cpu.allocate(task.required_memory_mb)
                        plans.append(
                            {
                                "job_id": job.job_id,
                                "task_id": task.task_id,
                                "assigned_device_id": cpu.id,
                                "assigned_backend": cpu.backend,
                                "frames": task.frames,
                                "reason": "cpu_fallback",
                            }
                        )
                        continue

                plans.append(
                    {
                        "job_id": job.job_id,
                        "task_id": task.task_id,
                        "assigned_device_id": None,
                        "assigned_backend": None,
                        "frames": task.frames,
                        "reason": "rejected",
                    }
                )

        return {"plans": plans, "devices": [d.to_dict() for d in sim_devices]}

