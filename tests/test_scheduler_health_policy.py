from 20_BLENDER_INTEGRATION.hero.telemetry import DeviceTelemetry
from 20_BLENDER_INTEGRATION.hero.scheduler import Scheduler, Device, Task, RenderJob


def test_scheduler_demotes_throttling_device_and_rejects_tasks():
    s = Scheduler()
    s.add_device(Device('gpu0', backend='CUDA', total_memory_mb=16000, free_memory_mb=8000, compute_score=1.0))
    s.add_device(Device('cpu0', backend='CPU', total_memory_mb=32000, free_memory_mb=16000, compute_score=0.5))

    t = DeviceTelemetry(window=3)
    # ingest a high temperature sample -> throttling
    t.ingest('gpu0', {'free_memory_mb': 8000, 'total_memory_mb': 16000, 'temperature_c': 120})

    # update scheduler from telemetry
    s.update_from_telemetry(t, ttl_seconds=5)

    dev_map = {d.id: d for d in s.devices}
    assert dev_map['gpu0'].health == 'throttling'
    assert dev_map['gpu0'].compute_score == 0.0

    # submit a job that requires GPU and does NOT allow CPU fallback
    task = Task('t1', required_memory_mb=1000, requires_gpu=True, allow_cpu_fallback=False)
    job = RenderJob('job1', [task], priority=10)
    s.submit(job)
    plan = s.dry_run()
    # since gpu0 has been demoted and CPU fallback not allowed, task should be rejected
    assert any(p['reason'] == 'rejected' for p in plan['plans'])


def test_scheduler_allows_cpu_fallback_when_enabled():
    s = Scheduler()
    s.add_device(Device('gpu0', backend='CUDA', total_memory_mb=16000, free_memory_mb=8000, compute_score=1.0))
    s.add_device(Device('cpu0', backend='CPU', total_memory_mb=32000, free_memory_mb=16000, compute_score=0.5))

    t = DeviceTelemetry(window=3)
    # throttled GPU
    t.ingest('gpu0', {'free_memory_mb': 8000, 'total_memory_mb': 16000, 'temperature_c': 120})
    s.update_from_telemetry(t, ttl_seconds=5)

    # job allows CPU fallback
    task = Task('t2', required_memory_mb=1000, requires_gpu=True, allow_cpu_fallback=True)
    job = RenderJob('job2', [task], priority=10)
    s.submit(job)
    plan = s.dry_run()
    # should be cpu_fallback assignment
    assert any(p['reason'] == 'cpu_fallback' for p in plan['plans'])
