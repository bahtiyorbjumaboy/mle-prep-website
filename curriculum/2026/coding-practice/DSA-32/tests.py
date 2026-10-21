from solution import TokenBucket


class FakeClock:
    def __init__(self, now=0.0):
        self.now = now
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.now


def _raises_value_error(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(solution.TokenBucket)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_burst_up_to_capacity_then_reject():
    clock = FakeClock()
    bucket = TokenBucket(capacity=3, refill_rate=1, clock=clock)
    assert [bucket.allow() for _ in range(4)] == [True, True, True, False]


def test_hand_computed_refill():
    clock = FakeClock()
    bucket = TokenBucket(capacity=2, refill_rate=1, clock=clock)
    assert bucket.allow() and bucket.allow() and not bucket.allow()
    clock.now = 1.0
    assert bucket.allow() and not bucket.allow()


def test_partial_refill_is_not_enough():
    clock = FakeClock()
    bucket = TokenBucket(capacity=4, refill_rate=2, clock=clock)
    assert bucket.allow(cost=4)
    clock.now = 0.5  # 1 token
    assert not bucket.allow(cost=2)
    assert bucket.allow(cost=1)
    clock.now = 1.25  # +1.5 tokens
    assert bucket.allow(cost=1.5)
    assert not bucket.allow(cost=0.5)


def test_exact_boundary_is_allowed():
    clock = FakeClock()
    bucket = TokenBucket(capacity=5, refill_rate=4, clock=clock)
    assert bucket.allow(cost=5)
    clock.now = 0.75  # exactly 3 tokens
    assert bucket.allow(cost=3)
    assert not bucket.allow(cost=1)


def test_floating_point_accumulation_at_boundary():
    # Twenty 1 ms refills at 50 tokens/s add exactly 1 token mathematically, but summing
    # the float increments gives 0.9999999999999999.
    clock = FakeClock()
    bucket = TokenBucket(capacity=1, refill_rate=50, clock=clock)
    assert bucket.allow()
    for step in range(1, 20):
        clock.now = step / 1000
        assert not bucket.allow(), step
    clock.now = 20 / 1000
    assert bucket.allow(), "a balance mathematically equal to the cost must be accepted"


def test_refill_is_capped_at_capacity():
    clock = FakeClock()
    bucket = TokenBucket(capacity=2, refill_rate=10, clock=clock)
    bucket.allow(cost=2)
    clock.now = 1000.0
    assert [bucket.allow() for _ in range(3)] == [True, True, False]


def test_rejected_request_consumes_nothing():
    clock = FakeClock()
    bucket = TokenBucket(capacity=3, refill_rate=1, clock=clock)
    assert bucket.allow(cost=2)
    assert not bucket.allow(cost=2)
    assert bucket.allow(cost=1)


def test_invalid_cost_raises():
    bucket = TokenBucket(capacity=2, refill_rate=1, clock=FakeClock())
    assert _raises_value_error(lambda: bucket.allow(cost=0))
    assert _raises_value_error(lambda: bucket.allow(cost=-1))
    assert _raises_value_error(lambda: bucket.allow(cost=3))
    assert bucket.allow(cost=2), "invalid requests must not consume tokens"


def test_invalid_configuration_raises():
    assert _raises_value_error(lambda: TokenBucket(capacity=0, refill_rate=1, clock=FakeClock()))
    assert _raises_value_error(lambda: TokenBucket(capacity=-1, refill_rate=1, clock=FakeClock()))
    assert _raises_value_error(lambda: TokenBucket(capacity=1, refill_rate=-1, clock=FakeClock()))


def test_uses_injected_clock_and_is_deterministic():
    def run():
        clock = FakeClock(100.0)
        bucket = TokenBucket(capacity=2, refill_rate=0.5, clock=clock)
        decisions = []
        for t in [100.0, 100.0, 100.0, 101.0, 102.0, 102.0, 106.0, 106.0, 106.0]:
            clock.now = t
            decisions.append(bucket.allow())
        return decisions, clock.calls

    first, calls = run()
    assert first == [True, True, False, False, True, False, True, True, False]
    assert calls > 0, "the bucket must read time from the injected clock"
    assert run()[0] == first


def test_clock_moving_backwards_removes_no_tokens():
    clock = FakeClock(10.0)
    bucket = TokenBucket(capacity=2, refill_rate=1, clock=clock)
    clock.now = 4.0
    assert bucket.allow() and bucket.allow(), "a full bucket stays full when the clock goes back"
    assert not bucket.allow()


def test_clock_moving_backwards_adds_no_tokens():
    clock = FakeClock(10.0)
    bucket = TokenBucket(capacity=2, refill_rate=1, clock=clock)
    assert bucket.allow(cost=2)
    clock.now = 5.0
    assert not bucket.allow()
    clock.now = 10.5  # only 0.5s past the latest observed time: not enough for 1 token
    assert not bucket.allow()
    clock.now = 11.0
    assert bucket.allow()


def test_default_clock_is_usable():
    bucket = TokenBucket(capacity=1, refill_rate=0.001)
    assert bucket.allow() is True
    assert bucket.allow() is False
