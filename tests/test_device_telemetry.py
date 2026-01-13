from 20_BLENDER_INTEGRATION.hero.telemetry import DeviceTelemetry


def test_ingest_and_snapshot_average():
    t = DeviceTelemetry(window=3)
    t.ingest('gpu0', {'free_memory_mb': 8000, 'compute_score': 1.0})
    t.ingest('gpu0', {'free_memory_mb': 7000, 'compute_score': 0.9})
    t.ingest('gpu0', {'free_memory_mb': 6000, 'compute_score': 0.8})
    snap = t.get_device('gpu0')
    assert 'free_memory_mb' in snap
    assert abs(snap['free_memory_mb'] - (8000 + 7000 + 6000)/3) < 1
    assert abs(snap['compute_score'] - (1.0 + 0.9 + 0.8)/3) < 1e-6


def test_snapshot_multiple_devices():
    t = DeviceTelemetry(window=2)
    t.ingest('gpuA', {'free_memory_mb': 5000, 'compute_score': 0.5})
    t.ingest('gpuB', {'free_memory_mb': 4000, 'compute_score': 0.4})
    s = t.snapshot()
    assert 'gpuA' in s and 'gpuB' in s
