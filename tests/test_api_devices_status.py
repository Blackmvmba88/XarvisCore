from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from 20_BLENDER_INTEGRATION.hero.api import app
from 20_BLENDER_INTEGRATION.hero.telemetry_ingest import on_telemetry_model, telemetry_window
from 20_BLENDER_INTEGRATION.hero.telemetry_model import TelemetrySample

client = TestClient(app)


def test_devices_status_empty():
    # ensure clean state
    telemetry_window._samples_per_device.clear()
    r = client.get("/devices/status")
    assert r.status_code == 200
    assert r.json() == []


def test_devices_status_and_device_endpoint():
    telemetry_window._samples_per_device.clear()
    now = datetime.utcnow()
    sample = TelemetrySample(ts=now, device_id="gpu-1", gpu_temp=60.0, gpu_memory_used_gb=4.0, gpu_memory_total_gb=16.0)
    telemetry_window.ingest(sample, now=now)

    r = client.get("/devices/status")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    dv = data[0]
    assert dv['device_id'] == 'gpu-1'

    r2 = client.get(f"/devices/gpu-1")
    assert r2.status_code == 200
    j = r2.json()
    assert j['device_id'] == 'gpu-1'
    assert j['health']['status'] in ('healthy', 'degraded')
