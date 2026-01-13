from datetime import datetime

from 20_BLENDER_INTEGRATION.hero.telemetry_model import TelemetrySample
from 20_BLENDER_INTEGRATION.hero.telemetry_window import TelemetryWindow
from 20_BLENDER_INTEGRATION.hero.scheduler import Scheduler, Device, Task, RenderJob


def test_scheduler_uses_window_health_to_demote_and_reject():
    s = Scheduler()
    s.add_device(Device('gpu0', backend='CUDA', total_memory_mb=16000, free_memory_mb=8000, compute_score=1.0))
    s.add_device(Device('cpu0', backend='CPU', total_memory_mb=32000, free_memory_mb=16000, compute_score=0.5))

    w = TelemetryWindow()
    ts = datetime.utcnow()
    # make a critical temp sample
    s_sample = TelemetrySample(ts=ts, device_id='gpu0', gpu_temp=120.0, gpu_memory_used_gb=2.0, gpu_memory_total_gb=16.0, is_throttling=True)
    w.ingest(s_sample, now=ts)

    s.update_from_window(w, now=ts)
    dev_map = {d.id: d for d in s.devices}
    assert dev_map['gpu0'].health == 'unhealthy' or dev_map['gpu0'].health == 'degraded'
    # submit a job requiring GPU without CPU fallback -> should be rejected
    task = Task('t-gpu', required_memory_mb=1000, requires_gpu=True, allow_cpu_fallback=False)
    job = RenderJob('job-w', [task], priority=10)
    s.submit(job)
    plan = s.dry_run()
    assert any(p['reason'] == 'rejected' for p in plan['plans'])


def test_scheduler_prefers_healthy_devices():
    s = Scheduler()
    s.add_device(Device('gpu0', backend='CUDA', total_memory_mb=16000, free_memory_mb=15000, compute_score=0.9))
    s.add_device(Device('gpu1', backend='CUDA', total_memory_mb=16000, free_memory_mb=15000, compute_score=0.8))

    w = TelemetryWindow()
    ts = datetime.utcnow()
    # gpu1 is degraded
    s1 = TelemetrySample(ts=ts, device_id='gpu1', gpu_temp=90.0, gpu_memory_used_gb=1.0, gpu_memory_total_gb=16.0, is_throttling=False)
    w.ingest(s1, now=ts)
    s.update_from_window(w, now=ts)

    task = Task('t1', required_memory_mb=500, requires_gpu=True, allow_cpu_fallback=False)
    job = RenderJob('job1', [task], priority=1)
    s.submit(job)
    plan = s.dry_run()

    # assigned to the healthier device (gpu0)
    assigned = [p for p in plan['plans'] if p['task_id'] == 't1'][0]
    assert assigned['assigned_device_id'] == 'gpu0'
