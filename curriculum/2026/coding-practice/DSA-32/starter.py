import time
from typing import Callable


class TokenBucket:
    """Token-bucket rate limiter with an injectable clock; never sleeps.

    The bucket starts full. Tokens refill continuously at `refill_rate` tokens per second
    of clock time, capped at `capacity`; refill is computed lazily when `allow` is called.

    Boundary rules:
        * A request is allowed when the available tokens are at least `cost`; exactly
          enough tokens is allowed. Tolerate floating-point error so a balance that is
          mathematically equal to `cost` is not rejected.
        * A rejected request consumes nothing.
        * If the clock moves backwards, no tokens are added or removed.
    """

    def __init__(self, capacity: float, refill_rate: float, clock: Callable[[], float] = time.monotonic) -> None:
        """Create a full bucket.

        Args:
            capacity: Maximum tokens; must be positive.
            refill_rate: Tokens added per second; must be nonnegative.
            clock: Zero-argument function returning the current time in seconds.

        Raises:
            ValueError: If `capacity <= 0` or `refill_rate < 0`.
        """
        raise NotImplementedError("TODO: implement DSA-32")

    def allow(self, cost: float = 1) -> bool:
        """Consume `cost` tokens and return `True` if available, else return `False`.

        Raises:
            ValueError: If `cost <= 0` or `cost > capacity` (it could never succeed).
        """
        raise NotImplementedError("TODO: implement DSA-32")
