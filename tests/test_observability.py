from datetime import datetime, timedelta

from 20_BLENDER_INTEGRATION.hero.telemetry_model import TelemetrySample
from 20_BLENDER_INTEGRATION.hero.telemetry_ingest import telemetry_window
from 20_BLENDER_INTEGRATION.hero.telemetry_observability import metrics


def test_sample_accept_and_ignore_counters():
    # reset state
    telemetry_window._samples_per_device.clear()
    metrics._counters.clear()
    metrics._ignore_reasons.clear()
    metrics._transitions.clear()

    now = datetime.utcnow()
    s1 = TelemetrySample(ts=now, device_id='gpuX', gpu_temp=60.0, gpu_memory_used_gb=2.0, gpu_memory_total_gb=16.0)
    telemetry_window.ingest(s1, now=now)
    assert metrics._counters.get('samples_accepted', 0) == 1

    # quick second sample should be rate-limited
    s2 = TelemetrySample(ts=now + timedelta(milliseconds=10), device_id='gpuX', gpu_temp=61.0, gpu_memory_used_gb=2.0, gpu_memory_total_gb=16.0)
    telemetry_window.ingest(s2, now=now + timedelta(milliseconds=10))
    assert metrics._counters.get('samples_ignored', 0) == 1
    assert metrics._ignore_reasons.get('rate_limited', 0) == 1


def test_health_transition_recorded():
    telemetry_window._samples_per_device.clear()
    metrics._counters.clear()
    metrics._ignore_reasons.clear()
    metrics._transitions.clear()

    t0 = datetime.utcnow()
    s_ok = TelemetrySample(ts=t0, device_id='gpuY', gpu_temp=60.0, gpu_memory_used_gb=2.0, gpu_memory_total_gb=16.0)
    telemetry_window.ingest(s_ok, now=t0)
    assert metrics._counters.get('samples_accepted', 0) == 1

    # now push a high temp sample -> transition to degraded/unhealthy
    t1 = t0 + timedelta(seconds=1)
    s_bad = TelemetrySample(ts=t1, device_id='gpuY', gpu_temp=120.0, gpu_memory_used_gb=2.0, gpu_memory_total_gb=16.0, is_throttling=True)
    telemetry_window.ingest(s_bad, now=t1)

    assert metrics._counters.get('health_transitions', 0) == 1
    assert len(metrics._transitions) == 1
    dev, old, new, ts_str, reason = metrics._transitions[0]
    assert dev == 'gpuY'
