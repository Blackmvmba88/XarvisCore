from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Deque, Dict, List, Optional


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


@dataclass
class TelemetrySample:
    ts: datetime
    device_id: str
    gpu_temp: float           # °C
    gpu_memory_used_gb: float
    gpu_memory_total_gb: float
    power_watts: Optional[float] = None
    is_throttling: bool = False


@dataclass
class Health:
    status: HealthStatus
    score: float              # 0.0–1.0
    reason: str
    flags: List[str]


@dataclass
class DeviceView:
    device_id: str
    last_ts: Optional[datetime]
    avg_temp: Optional[float]
    max_temp: Optional[float]
    mem_pressure: Optional[float]  # [0,1]
    sample_count: int
    health: Health
