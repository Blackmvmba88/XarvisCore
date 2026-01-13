"""Simple ingestion helper that holds a global TelemetryWindow instance and helper functions.

The scheduler or external processes should call `on_telemetry(sample_dict)` or
`on_telemetry_model(TelemetrySampleModel)` to route samples into the rolling window.

The API will query `get_all_device_views()` / `get_device_view()`.
"""
from typing import Dict, Any, Optional

from .telemetry_window import TelemetryWindow
from .telemetry_model import TelemetrySample
from .pydantic_models import TelemetrySampleModel

# single, shared window for the scheduler service
telemetry_window = TelemetryWindow()


def on_telemetry_dict(sample: Dict[str, Any]) -> None:
    """Accept a raw dict (validated by caller) and ingest it."""
    m = TelemetrySampleModel(**sample)
    on_telemetry_model(m)


def on_telemetry_model(sample: TelemetrySampleModel, now: Optional=None) -> None:
    s = TelemetrySample(
        ts=sample.ts,
        device_id=sample.device_id,
        gpu_temp=sample.gpu_temp,
        gpu_memory_used_gb=sample.gpu_memory_used_gb,
        gpu_memory_total_gb=sample.gpu_memory_total_gb,
        power_watts=sample.power_watts,
        is_throttling=bool(sample.is_throttling),
    )
    telemetry_window.ingest(s, now=now or s.ts)


def get_all_device_views(now: Optional=None):
    # return DeviceView objects (not serialized)
    ids = list(telemetry_window._samples_per_device.keys())
    return [telemetry_window.get_device_view(d, now=now) for d in ids]


def get_device_view(device_id: str, now: Optional=None):
    return telemetry_window.get_device_view(device_id, now=now)


def get_device_history(device_id: str, limit: Optional[int] = 100, since: Optional=None):
    """Return list of TelemetrySample objects (most recent first) for device_id.
    `since` can be a datetime; if provided, only samples with ts >= since are returned.
    """
    buf = telemetry_window._samples_per_device.get(device_id)
    if not buf:
        return []
    samples = list(buf)
    # apply since filter
    if since is not None:
        try:
            from datetime import datetime

            samples = [s for s in samples if s.ts >= since]
        except Exception:
            pass
    # most recent first
    samples = list(reversed(samples))
    if limit is not None:
        samples = samples[:int(limit)]
    return samples

