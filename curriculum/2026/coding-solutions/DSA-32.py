import time
from typing import Callable

_EPSILON = 1e-9


class TokenBucket:
    """Lazily refilled token bucket with an injectable clock."""

    def __init__(self, capacity: float, refill_rate: float, clock: Callable[[], float] = time.monotonic) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate < 0:
            raise ValueError("refill_rate must be nonnegative")
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._clock = clock
        self._tokens = float(capacity)
        self._last = clock()

    def _refill(self) -> None:
        now = self._clock()
        # Ignore backwards clock movement; only forward progress earns tokens.
        if now > self._last:
            self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.refill_rate)
        self._last = max(self._last, now)

    def allow(self, cost: float = 1) -> bool:
        if cost <= 0 or cost > self.capacity:
            raise ValueError(f"cost must be in (0, {self.capacity}]")
        self._refill()
        if self._tokens + _EPSILON >= cost:
            self._tokens = max(0.0, self._tokens - cost)
            return True
        return False
