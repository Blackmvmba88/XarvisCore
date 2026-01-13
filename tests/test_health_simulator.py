from datetime import datetime, timedelta

from 20_BLENDER_INTEGRATION.hero.telemetry_model import TelemetrySample
from 20_BLENDER_INTEGRATION.hero.telemetry_ingest import telemetry_window
from 20_BLENDER_INTEGRATION.hero.scheduler import Scheduler, Device, Task, RenderJob


def test_health_flips_and_scheduler_replans():
    # prepare scheduler and devices
    s = Scheduler()
    s.add_device(Device('gpu0', backend='CUDA', total_memory_mb=16000, free_memory_mb=16000, compute_score=1.0))
    s.add_device(Device('cpu0', backend='CPU', total_memory_mb=32000, free_memory_mb=32000, compute_score=0.5))

    # start healthy
    ts = datetime.utcnow()
    healthy = TelemetrySample(ts=ts, device_id='gpu0', gpu_temp=60.0, gpu_memory_used_gb=2.0, gpu_memory_total_gb=16.0)
    telemetry_window.ingest(healthy, now=ts)
    s.update_from_window(telemetry_window, now=ts)

    # submit job requiring GPU, no fallback
    task = Task('t1', required_memory_mb=1000, requires_gpu=True, allow_cpu_fallback=False)
    job = RenderJob('job1', [task], priority=1)
    s.submit(job)
    plan_ok = s.dry_run()
    assert any(p['assigned_device_id'] == 'gpu0' for p in plan_ok['plans'])

    # now device degrades (throttling/high temp)
    ts2 = ts + timedelta(seconds=1)
    bad = TelemetrySample(ts=ts2, device_id='gpu0', gpu_temp=120.0, gpu_memory_used_gb=2.0, gpu_memory_total_gb=16.0, is_throttling=True)
    telemetry_window.ingest(bad, now=ts2)
    s.update_from_window(telemetry_window, now=ts2)

    plan_after = s.dry_run()
    # job should be rejected because gpu unhealthy and no cpu fallback
    assert any(p['reason'] == 'rejected' for p in plan_after['plans'])

    # enable CPU fallback and resubmit
    s = Scheduler()
    s.add_device(Device('gpu0', backend='CUDA', total_memory_mb=16000, free_memory_mb=16000, compute_score=1.0))
    s.add_device(Device('cpu0', backend='CPU', total_memory_mb=32000, free_memory_mb=32000, compute_score=0.5))
    telemetry_window.ingest(bad, now=ts2)
    s.update_from_window(telemetry_window, now=ts2)
    task2 = Task('t2', required_memory_mb=1000, requires_gpu=True, allow_cpu_fallback=True)
    job2 = RenderJob('job2', [task2], priority=1)
    s.submit(job2)
    plan_fallback = s.dry_run()
    assert any(p['reason'] == 'cpu_fallback' for p in plan_fallback['plans'])
