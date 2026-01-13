from collections import deque
from typing import Dict, Deque, Any, Optional
from datetime import datetime, timezone


class DeviceTelemetry:
    """Simple telemetry ingestion with rolling window aggregation for devices.

    Usage:
      t = DeviceTelemetry(window=5)
      t.ingest('gpu0', {'free_memory_mb': 7000, 'compute_score': 0.9, 'temperature_c': 65})
      snap = t.snapshot()  # latest aggregated values per device
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
