from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class HealthModel(BaseModel):
    status: str
    score: float
    reason: str
    flags: List[str]


class DeviceViewModel(BaseModel):
    device_id: str
    last_ts: Optional[datetime]
    avg_temp: Optional[float]
    max_temp: Optional[float]
    mem_pressure: Optional[float]
    sample_count: int
    health: HealthModel


class TelemetrySampleModel(BaseModel):
    ts: datetime
    device_id: str
    gpu_temp: float
    gpu_memory_used_gb: float
    gpu_memory_total_gb: float
    is_throttling: Optional[bool] = False
    power_watts: Optional[float] = None


class DeviceViewWithHistory(DeviceViewModel):
    history: List[TelemetrySampleModel] = []

