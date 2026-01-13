from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from 20_BLENDER_INTEGRATION.hero.api import app
from 20_BLENDER_INTEGRATION.hero.telemetry_ingest import telemetry_window, get_device_history
from 20_BLENDER_INTEGRATION.hero.telemetry_model import TelemetrySample

client = TestClient(app)


def test_device_history_endpoint():
    telemetry_window._samples_per_device.clear()
    now = datetime.utcnow()
    for i in range(5):
        s = TelemetrySample(ts=now + timedelta(seconds=i), device_id='gpu-z', gpu_temp=60 + i, gpu_memory_used_gb=2.0 + i, gpu_memory_total_gb=16.0)
        telemetry_window.ingest(s, now=s.ts)

    r = client.get('/devices/gpu-z/history')
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 5
    # check order: most recent first
    assert data[0]['gpu_temp'] == 64


def test_devices_status_history_endpoint():
    telemetry_window._samples_per_device.clear()
    now = datetime.utcnow()
    for i in range(3):
        s = TelemetrySample(ts=now + timedelta(seconds=i), device_id='gpu-abc', gpu_temp=60 + i, gpu_memory_used_gb=2.0 + i, gpu_memory_total_gb=16.0)
        telemetry_window.ingest(s, now=s.ts)

    r = client.get('/devices/status/history?limit=2')
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # find gpu-abc
    found = [d for d in data if d['device_id'] == 'gpu-abc']
    assert found
    assert len(found[0]['history']) == 2
