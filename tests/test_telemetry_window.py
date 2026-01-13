import pytest
from datetime import datetime, timedelta

from 20_BLENDER_INTEGRATION.hero.telemetry_window import TelemetryWindow
from 20_BLENDER_INTEGRATION.hero.telemetry_model import TelemetrySample, HealthStatus
from 20_BLENDER_INTEGRATION.hero import telemetry_config as config

BASE_TS = datetime(2024, 1, 1, 0, 0, 0)


def make_sample(
    ts: datetime,
    gpu_temp: float = 60.0,
    used_gb: float = 8.0,
    total_gb: float = 24.0,
    device_id: str = "gpu-0",
    is_throttling: bool = False,
):
    return TelemetrySample(
        ts=ts,
        device_id=device_id,
        gpu_temp=gpu_temp,
        gpu_memory_used_gb=used_gb,
        gpu_memory_total_gb=total_gb,
        is_throttling=is_throttling,
    )


def test_offline_device_has_no_telemetry():
    w = TelemetryWindow()
    view = w.get_device_view("gpu-0", now=BASE_TS)
    assert view.health.status == HealthStatus.OFFLINE
    assert "no_samples" in view.health.flags


def test_stale_data_marks_unhealthy():
    w = TelemetryWindow()
    s = make_sample(BASE_TS)
    w.ingest(s, now=BASE_TS)

    now = BASE_TS + config.STALE_DEVICE_TTL + timedelta(milliseconds=1)
    view = w.get_device_view("gpu-0", now=now)
    assert view.health.status == HealthStatus.UNHEALTHY
    assert view.health.reason == "stale_telemetry"


def test_sampling_rate_discards_too_frequent_samples():
    w = TelemetryWindow()
    s1 = make_sample(BASE_TS)
    s2 = make_sample(BASE_TS + timedelta(milliseconds=10))  # faster than MIN_SAMPLE_INTERVAL

    w.ingest(s1, now=BASE_TS)
    w.ingest(s2, now=BASE_TS + timedelta(milliseconds=10))

    view = w.get_device_view("gpu-0", now=BASE_TS + timedelta(milliseconds=50))
    assert view.sample_count == 1  # s2 was discarded


def test_throttling_sets_degraded():
    w = TelemetryWindow()
    s = make_sample(BASE_TS, is_throttling=True)
    w.ingest(s, now=BASE_TS)

    view = w.get_device_view("gpu-0", now=BASE_TS + timedelta(milliseconds=100))
    assert view.health.status == HealthStatus.DEGRADED
    assert "throttling" in view.health.flags


def test_memory_pressure_warn_and_crit():
    w = TelemetryWindow()

    # WARN
    used_warn = 0.9 * 24.0
    s_warn = make_sample(BASE_TS, used_gb=used_warn, total_gb=24.0)
    w.ingest(s_warn, now=BASE_TS)
    view_warn = w.get_device_view("gpu-0", now=BASE_TS + timedelta(milliseconds=100))
    assert view_warn.health.status in (HealthStatus.DEGRADED, HealthStatus.UNHEALTHY)
    assert any("mem_" in f for f in view_warn.health.flags)

    # CRIT
    w = TelemetryWindow()
    used_crit = 0.99 * 24.0
    s_crit = make_sample(BASE_TS, used_gb=used_crit, total_gb=24.0)
    w.ingest(s_crit, now=BASE_TS)
    view_crit = w.get_device_view("gpu-0", now=BASE_TS + timedelta(milliseconds=100))
    assert view_crit.health.status == HealthStatus.UNHEALTHY
    assert "mem_crit" in view_crit.health.flags
