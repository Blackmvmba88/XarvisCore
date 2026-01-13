from datetime import datetime
from typing import Dict, Optional
from collections import deque

from .telemetry_model import TelemetrySample, DeviceView, Health, HealthStatus
from . import telemetry_config as config


class TelemetryWindow:
    """
    Maintains a time window of samples per device and computes health.
    """

    def __init__(self):
        self._samples_per_device: Dict[str, deque[TelemetrySample]] = {}
        self._last_accepted_ts: Dict[str, datetime] = {}

    def ingest(self, sample: TelemetrySample, now: Optional[datetime] = None) -> None:
        now = now or sample.ts

        # 1. TTL: if the sample is already too old, drop it
        if now - sample.ts > config.TELEMETRY_TTL:
            return

        # 2. sampling_rate: drop if samples arrive too fast
        last_ts = self._last_accepted_ts.get(sample.device_id)
        if last_ts is not None and (sample.ts - last_ts).total_seconds() < config.TELEMETRY_MIN_SAMPLE_INTERVAL.total_seconds():
            return

        # 3. store
        buf = self._samples_per_device.setdefault(sample.device_id, deque())
        buf.append(sample)
        self._last_accepted_ts[sample.device_id] = sample.ts

        # 4. time-based rolling window
        cutoff_ts = now - config.TELEMETRY_WINDOW
        while buf and buf[0].ts < cutoff_ts:
            buf.popleft()

        # 5. size bound
        while len(buf) > config.TELEMETRY_MAX_SAMPLES:
            buf.popleft()

    def get_device_view(self, device_id: str, now: Optional[datetime] = None) -> DeviceView:
        now = now or datetime.utcnow()
        buf = self._samples_per_device.get(device_id)

        if not buf:
            health = Health(
                status=HealthStatus.OFFLINE,
                score=0.0,
                reason="no_telemetry",
                flags=["no_samples"],
            )
            return DeviceView(
                device_id=device_id,
                last_ts=None,
                avg_temp=None,
                max_temp=None,
                mem_pressure=None,
                sample_count=0,
                health=health,
            )

        last_ts = buf[-1].ts
        dt_last = now - last_ts

        if dt_last > config.STALE_DEVICE_TTL:
            health = Health(
                status=HealthStatus.UNHEALTHY,
                score=0.1,
                reason="stale_telemetry",
                flags=["stale", f"stale_ms={int(dt_last.total_seconds()*1000)}"],
            )
            return DeviceView(
                device_id=device_id,
                last_ts=last_ts,
                avg_temp=None,
                max_temp=None,
                mem_pressure=None,
                sample_count=len(buf),
                health=health,
            )

        temps = [s.gpu_temp for s in buf]
        mem_pressures = [
            s.gpu_memory_used_gb / s.gpu_memory_total_gb
            for s in buf
            if s.gpu_memory_total_gb > 0
        ]
        avg_temp = sum(temps) / len(temps)
        max_temp = max(temps)
        avg_mem_pressure = sum(mem_pressures) / len(mem_pressures) if mem_pressures else None

        health = self._evaluate_health(
            max_temp=max_temp,
            avg_mem_pressure=avg_mem_pressure,
            is_throttling_any=any(s.is_throttling for s in buf),
        )

        return DeviceView(
            device_id=device_id,
            last_ts=last_ts,
            avg_temp=avg_temp,
            max_temp=max_temp,
            mem_pressure=avg_mem_pressure,
            sample_count=len(buf),
            health=health,
        )

    def _evaluate_health(
        self,
        max_temp: float,
        avg_mem_pressure: Optional[float],
        is_throttling_any: bool,
    ) -> Health:
        flags = []

        # Temperature
        if max_temp >= config.GPU_TEMP_CRIT:
            flags.append("temp_crit")
        elif max_temp >= config.GPU_TEMP_WARN:
            flags.append("temp_warn")

        # Memory
        if avg_mem_pressure is not None:
            if avg_mem_pressure >= config.GPU_MEM_PRESSURE_CRIT:
                flags.append("mem_crit")
            elif avg_mem_pressure >= config.GPU_MEM_PRESSURE_WARN:
                flags.append("mem_warn")

        # Throttling
        if is_throttling_any:
            flags.append("throttling")

        if "temp_crit" in flags or "mem_crit" in flags:
            status = HealthStatus.UNHEALTHY
            score = 0.2
            reason = "critical_limits"
        elif "throttling" in flags or "temp_warn" in flags or "mem_warn" in flags:
            status = HealthStatus.DEGRADED
            score = 0.6
            reason = "degraded"
        else:
            status = HealthStatus.HEALTHY
            score = 1.0
            reason = "ok"

        if not flags:
            flags = ["ok"]

        return Health(
            status=status,
            score=score,
            reason=reason,
            flags=flags,
        )
