from 20_BLENDER_INTEGRATION.hero.telemetry import DeviceTelemetry
from 20_BLENDER_INTEGRATION.hero.scheduler import Scheduler, Task, RenderJob


def test_scheduler_uses_telemetry_for_allocation():
    s = Scheduler()
    # initially one GPU with 8000 free
    s.register_devices([{'id': 'gpu0', 'backend': 'CUDA', 'total_memory_mb': 16000, 'free_memory_mb': 8000, 'compute_score': 1.0},
                        {'id': 'cpu0', 'backend': 'CPU', 'total_memory_mb': 16000, 'free_memory_mb': 16000, 'compute_score': 0.1}])

    t = Task('t1', required_memory_mb=7000, requires_gpu=True, frames=1, priority=0, allow_cpu_fallback=False)
    s.submit(RenderJob('job1', tasks=[t], priority=0))
    # regular plan assigns to gpu0
    plan1 = s.dry_run()
    assert plan1['plans'][0]['assigned_device_id'] == 'gpu0'

    # now telemetry reports gpu0 free memory dropped to 1000 -> task should be rejected
    tel = DeviceTelemetry(window=3)
    tel.ingest('gpu0', {'free_memory_mb': 1000, 'compute_score': 1.0})
    s.update_from_telemetry(tel.snapshot())
    plan2 = s.dry_run()
    assert plan2['plans'][0]['reason'] == 'rejected'
