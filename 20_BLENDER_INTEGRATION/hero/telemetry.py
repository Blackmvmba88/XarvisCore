from collections import deque
from typing import Dict, Deque, Any, Optional
from datetime import datetime, timezone


class DeviceTelemetry:
    """Telemetry ingestion with rolling window aggregation and health assessment.

    Usage:
      t = DeviceTelemetry(window=5)
      t.ingest('gpu0', {'free_memory_mb': 7000, 'compute_score': 0.9, 'temperature_c': 65})
      snap = t.snapshot()  # latest aggregated values per device
      health = t.assess_health('gpu0', ttl_seconds=5)
    """

    def __init__(self, window: int = 5):
        self.window = max(1, int(window))
        # store per-device queues of metrics dicts
        self._queues: Dict[str, Deque[Dict[str, Any]]] = {}

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def ingest(self, device_id: str, metrics: Dict[str, Any], ts: Optional[str] = None):
        """Ingest a telemetry sample for device_id.
        metrics keys expected: free_memory_mb (int), total_memory_mb (int, optional), compute_score (float), occupancy (0..1 float), temperature_c (float)
        """
        if device_id not in self._queues:
            self._queues[device_id] = deque(maxlen=self.window)
        sample = dict(metrics)
        sample['_ts'] = ts or self._now()
        self._queues[device_id].append(sample)

    def _aggregate_queue(self, q: Deque[Dict[str, Any]]) -> Dict[str, Any]:
        if not q:
            return {}
        agg: Dict[str, Any] = {}
        # numeric keys: compute simple mean
        numeric_keys = set()
        for s in q:
            for k, v in s.items():
                if k == '_ts':
                    continue
                if isinstance(v, (int, float)):
                    numeric_keys.add(k)
        for k in numeric_keys:
            vals = [s[k] for s in q if k in s]
            if vals:
                agg[k] = sum(vals) / len(vals)
        # include last timestamp
        agg['_latest_ts'] = q[-1].get('_ts')
        return agg

    def snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Return aggregated snapshot per device id."""
        out: Dict[str, Dict[str, Any]] = {}
        for dev, q in self._queues.items():
            out[dev] = self._aggregate_queue(q)
        return out

    def get_device(self, device_id: str) -> Dict[str, Any]:
        q = self._queues.get(device_id, deque())
        return self._aggregate_queue(q)

    def clear(self):
        self._queues.clear()

    def assess_health(self, device_id: str, ttl_seconds: int = 5, temp_threshold: float = 95.0, mem_pressure_ratio: float = 0.1, occupancy_threshold: float = 0.95) -> Dict[str, str]:
        """Assess device health and return dict: {'health': 'healthy'|'offline'|'throttling'|'memory_pressure'|'high_occupancy', 'reason': <str>}"""
        import time
        q = self._queues.get(device_id)
        if not q or len(q) == 0:
            return {'health': 'offline', 'reason': 'no_samples'}
        latest = q[-1]
        ts = latest.get('_ts')
        try:
            # parse timestamp
            t_latest = datetime.fromisoformat(ts)
            age_seconds = (datetime.now(timezone.utc) - t_latest).total_seconds()
        except Exception:
            age_seconds = float('inf')
        if age_seconds > ttl_seconds:
            return {'health': 'offline', 'reason': f'stale_data_{age_seconds:.1f}s'}
        # check temperature
        temp = latest.get('temperature_c')
        if temp is not None:
            try:
                if float(temp) >= float(temp_threshold):
                    return {'health': 'throttling', 'reason': f'temp_{temp}C'}
            except Exception:
                pass
        # check memory pressure (needs total_memory or we check absolute free)
        free = latest.get('free_memory_mb')
        total = latest.get('total_memory_mb')
        if free is not None and total is not None:
            try:
                if float(total) > 0 and (float(free) / float(total)) <= float(mem_pressure_ratio):
                    return {'health': 'memory_pressure', 'reason': f'free={free} total={total}'}
            except Exception:
                pass
        # check occupancy
        occ = latest.get('occupancy')
        if occ is not None:
            try:
                if float(occ) >= float(occupancy_threshold):
                    return {'health': 'high_occupancy', 'reason': f'occ={occ}'}
            except Exception:
                pass
        return {'health': 'healthy', 'reason': 'ok'}

    def snapshot_with_health(self, ttl_seconds: int = 5, temp_threshold: float = 95.0, mem_pressure_ratio: float = 0.1, occupancy_threshold: float = 0.95) -> Dict[str, Dict[str, Any]]:
        out = self.snapshot()
        for dev in list(out.keys()):
            h = self.assess_health(dev, ttl_seconds=ttl_seconds, temp_threshold=temp_threshold, mem_pressure_ratio=mem_pressure_ratio, occupancy_threshold=occupancy_threshold)
            out[dev]['_health'] = h['health']
            out[dev]['_health_reason'] = h['reason']
        return out
