from 20_BLENDER_INTEGRATION.hero.scheduler import Scheduler, Device, Task, RenderJob


def test_scheduler_rejects_jobs_if_no_gpu_and_job_requires_gpu():
    s = Scheduler()
    # only CPU device
    s.register_devices([{'id': 'cpu0', 'backend': 'CPU', 'total_memory_mb': 16000, 'free_memory_mb': 16000, 'compute_score': 0.1}])

    t = Task('t1', required_memory_mb=1000, requires_gpu=True, frames=1, priority=0, allow_cpu_fallback=False)
    job = RenderJob('job1', tasks=[t], priority=0)
    s.submit(job)

    plan = s.dry_run()
    assert plan['plans'][0]['reason'] == 'rejected'
    assert plan['plans'][0]['assigned_device_id'] is None


def test_scheduler_respects_priority_ordering():
    s = Scheduler()
    s.register_devices([
        {'id': 'gpu0', 'backend': 'CUDA', 'total_memory_mb': 16000, 'free_memory_mb': 16000, 'compute_score': 1.0},
    ])

    low = Task('low', required_memory_mb=100, requires_gpu=True, frames=1, priority=1)
    high = Task('high', required_memory_mb=100, requires_gpu=True, frames=1, priority=10)
    j1 = RenderJob('job_low', tasks=[low], priority=1)
    j2 = RenderJob('job_high', tasks=[high], priority=10)
    s.submit(j1)
    s.submit(j2)

    plan = s.dry_run()
    # high priority task should appear before low priority in plans
    ids = [p['task_id'] for p in plan['plans']]
    assert ids[0] == 'high'


def test_scheduler_coalesces_small_jobs_on_same_device():
    s = Scheduler()
    s.register_devices([
        {'id': 'gpu0', 'backend': 'CUDA', 'total_memory_mb': 8000, 'free_memory_mb': 8000, 'compute_score': 1.0},
    ])

    t1 = Task('t1', required_memory_mb=1000, requires_gpu=True, frames=1, priority=0)
    t2 = Task('t2', required_memory_mb=1000, requires_gpu=True, frames=1, priority=0)
    j = RenderJob('job1', tasks=[t1, t2], priority=0)
    s.submit(j)

    plan = s.dry_run()
    assert plan['plans'][0]['assigned_device_id'] == 'gpu0'
    assert plan['plans'][1]['assigned_device_id'] == 'gpu0'


def test_scheduler_fallback_to_cpu_when_allowed():
    s = Scheduler()
    s.register_devices([
        {'id': 'cpu0', 'backend': 'CPU', 'total_memory_mb': 8000, 'free_memory_mb': 8000, 'compute_score': 0.2},
    ])

    t = Task('t1', required_memory_mb=500, requires_gpu=True, frames=1, priority=0, allow_cpu_fallback=True)
    j = RenderJob('job1', tasks=[t], priority=0)
    s.submit(j)

    plan = s.dry_run()
    assert plan['plans'][0]['reason'] == 'cpu_fallback'
    assert plan['plans'][0]['assigned_device_id'] == 'cpu0'
