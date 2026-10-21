import random

from solution import combination_sum


def _normalize(combos):
    # Keep multiplicity so the same combination in two orders is detected.
    return sorted(tuple(sorted(c)) for c in combos)


def _brute(candidates, target):
    out = set()

    def go(remaining, combo):
        if remaining == 0:
            out.add(tuple(sorted(combo)))
            return
        for c in candidates:
            if c <= remaining:
                go(remaining - c, combo + [c])

    go(target, [])
    return sorted(out)


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "combination_sum")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    assert _normalize(combination_sum([2, 3, 6, 7], 7)) == [(2, 2, 3), (7,)]


def test_reuse_of_candidates():
    assert _normalize(combination_sum([2, 3, 5], 8)) == [(2, 2, 2, 2), (2, 3, 3), (3, 5)]
    assert _normalize(combination_sum([1], 3)) == [(1, 1, 1)]


def test_unreachable_target():
    assert combination_sum([2], 1) == []
    assert combination_sum([4, 6], 9) == []


def test_candidates_larger_than_target_are_ignored():
    assert _normalize(combination_sum([10, 3], 6)) == [(3, 3)]


def test_permutations_are_not_duplicates():
    # Restarting the loop at index 0 emits (2, 3, 2) and (3, 2, 2) as well.
    result = _normalize(combination_sum([3, 2], 7))
    assert result == [(2, 2, 3)]


def test_unsorted_candidates():
    assert _normalize(combination_sum([7, 3, 6, 2], 7)) == [(2, 2, 3), (7,)]


def test_returned_combinations_are_independent_lists():
    result = combination_sum([2, 3, 5], 8)
    assert len({id(c) for c in result}) == len(result)
    assert _normalize(result) == [(2, 2, 2, 2), (2, 3, 3), (3, 5)]


def test_every_combination_sums_to_target_on_random_inputs():
    rng = random.Random(16)
    for _ in range(100):
        candidates = rng.sample(range(1, 12), rng.randint(1, 5))
        target = rng.randint(1, 20)
        result = combination_sum(list(candidates), target)
        assert all(sum(c) == target and set(c) <= set(candidates) for c in result)
        assert _normalize(result) == _brute(candidates, target), (candidates, target)
