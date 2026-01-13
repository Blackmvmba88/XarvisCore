from datetime import datetime, timedelta, timezone

from 20_BLENDER_INTEGRATION.hero.telemetry import DeviceTelemetry


def iso_n_seconds_ago(n):
    return (datetime.now(timezone.utc) - timedelta(seconds=n)).isoformat()


def test_offline_device_no_samples():
    t = DeviceTelemetry(window=3)
    health = t.assess_health('gpuX')
    assert health['health'] == 'offline'
    assert 'no_samples' in health['reason']


def test_stale_data_is_offline():
    t = DeviceTelemetry(window=3)
    t.ingest('gpu0', {'free_memory_mb': 8000, 'total_memory_mb': 16384, 'temperature_c': 60}, ts=iso_n_seconds_ago(10))
    # TTL default is 5 seconds, so a sample 10s ago should mark offline
    health = t.assess_health('gpu0', ttl_seconds=5)
    assert health['health'] == 'offline'
    assert 'stale_data' in health['reason']


def test_throttling_flag():
    t = DeviceTelemetry(window=3)
    t.ingest('gpu1', {'free_memory_mb': 7000, 'total_memory_mb': 16384, 'temperature_c': 120}, ts=iso_n_seconds_ago(1))
    health = t.assess_health('gpu1', ttl_seconds=5, temp_threshold=100.0)
    assert health['health'] == 'throttling'
    assert 'temp' in health['reason']


def test_memory_pressure_flag():
    t = DeviceTelemetry(window=3)
    # free 200MB out of 16000 -> pressure
    t.ingest('gpu2', {'free_memory_mb': 200, 'total_memory_mb': 16000, 'temperature_c': 40}, ts=iso_n_seconds_ago(1))
    health = t.assess_health('gpu2', ttl_seconds=5, mem_pressure_ratio=0.05)
    # 200/16000 = 0.0125 <= 0.05 -> memory pressure
    assert health['health'] == 'memory_pressure'
    assert 'free=' in health['reason']
