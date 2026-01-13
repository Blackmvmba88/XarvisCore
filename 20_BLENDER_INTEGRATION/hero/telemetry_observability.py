"""Observability helpers: in-memory counters, health transition events, structured logging.

This is intentionally lightweight and test-friendly. It exposes a simple API for the rest
of the telemetry stack and a JSON-friendly `get_metrics()` snapshot used by `/metrics` endpoint.
"""
from collections import defaultdict, deque
from datetime import datetime
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class Observability:
    def __init__(self):
        # counters by name
        self._counters: Dict[str, int] = defaultdict(int)
        # recent health transitions (device_id, old, new, ts, reason)
        self._transitions: deque[Tuple[str, str, str, str, str]] = deque(maxlen=256)
        # sample verdict reasons (ignored reasons count)
        self._ignore_reasons: Dict[str, int] = defaultdict(int)

    def incr(self, name: str, n: int = 1):
        self._counters[name] += int(n)

    def record_ignore(self, reason: str):
        self._ignore_reasons[reason] += 1
        self.incr('samples_ignored')

    def record_accept(self):
        self.incr('samples_accepted')

    def record_health_transition(self, device_id: str, old: str, new: str, reason: str = ''):
        ts = datetime.utcnow().isoformat()
        self._transitions.append((device_id, old, new, ts, reason))
        self.incr('health_transitions')
        # structured log so it shows in logs as well
        logger.info('HEALTH_TRANSITION', extra={'device_id': device_id, 'old': old, 'new': new, 'reason': reason, 'ts': ts})

    def snapshot(self) -> Dict[str, Any]:
        return {
            'counters': dict(self._counters),
            'ignore_reasons': dict(self._ignore_reasons),
            'recent_transitions': list(self._transitions),
        }


# singleton for the service
metrics = Observability()
