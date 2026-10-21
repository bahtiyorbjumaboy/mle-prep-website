import hashlib

import numpy as np

from solution import check_leakage, group_hash_split, grouped_split, hash_bucket, temporal_split


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _sha_bucket(group, salt="", n=10_000):
    return int(hashlib.sha256(f"{salt}:{group}".encode("utf-8")).hexdigest(), 16) % n


def _groups(n_groups=40, seed=0):
    rng = np.random.default_rng(seed)
    sizes = rng.integers(1, 6, size=n_groups)
    return [f"user_{g}" for g, s in enumerate(sizes) for _ in range(s)]


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("hash_bucket", "group_hash_split", "grouped_split", "temporal_split", "check_leakage"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_hash_bucket_is_the_stable_sha256_contract():
    for group, salt in [("user_1", ""), ("user_1", "v2"), (12345, ""), ("é-ünicode", "s")]:
        assert hash_bucket(group, salt) == _sha_bucket(group, salt)
    assert hash_bucket("abc", n_buckets=7) == _sha_bucket("abc", n=7)


def test_does_not_use_builtin_hash():
    import ast
    import inspect
    import solution
    tree = ast.parse(inspect.getsource(solution))
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "hash" not in calls, "built-in hash() of str is randomized per process (PYTHONHASHSEED)"


def test_group_hash_split_matches_contract_and_never_splits_groups():
    groups = _groups()
    is_test = group_hash_split(groups, 0.3, salt="exp1")
    assert isinstance(is_test, np.ndarray) and is_test.dtype == np.bool_ and is_test.shape == (len(groups),)
    expected = np.array([_sha_bucket(g, "exp1") < 3000 for g in groups])
    assert np.array_equal(is_test, expected)
    for g in set(groups):
        sides = {bool(t) for gg, t in zip(groups, is_test) if gg == g}
        assert len(sides) == 1


def test_group_hash_split_threshold_boundary_is_exclusive():
    boundary = next(f"g{i}" for i in range(200_000) if _sha_bucket(f"g{i}") == 2500)
    assert group_hash_split([boundary], 0.25).tolist() == [False]  # 2500 < 2500 is False
    assert group_hash_split([boundary], 0.2501).tolist() == [True]


def test_group_hash_split_stable_when_new_groups_arrive_and_monotone_in_fraction():
    old = _groups(30, seed=1)
    new = old + [f"new_{i}" for i in range(50)]
    a = group_hash_split(old, 0.25)
    b = group_hash_split(new, 0.25)
    assert np.array_equal(a, b[: len(old)])
    shuffled = list(reversed(new))
    assert np.array_equal(group_hash_split(shuffled, 0.25), b[::-1])
    bigger = group_hash_split(new, 0.5)
    assert np.all(bigger[b]), "raising test_fraction only moves groups from train to test"
    assert _raises(ValueError, group_hash_split, new, 0.0)
    assert _raises(ValueError, group_hash_split, new, 1.0)


def test_grouped_split_contract_counts_groups_not_rows():
    groups = ["giant"] * 90 + ["a", "b", "c", "d", "e", "f", "g", "h", "i"] + ["j"]
    is_test = grouped_split(groups, 0.2, seed=3)
    distinct = sorted(set(groups))
    order = np.random.default_rng(3).permutation(len(distinct))
    test_groups = {distinct[i] for i in order[:2]}  # round(0.2 * 11) = 2
    assert np.array_equal(is_test, np.array([g in test_groups for g in groups]))
    assert len({g for g, t in zip(groups, is_test) if t}) == 2


def test_grouped_split_deterministic_and_row_order_invariant():
    groups = _groups(25, seed=2)
    a = grouped_split(groups, 0.3, seed=11)
    assert np.array_equal(a, grouped_split(groups, 0.3, seed=11))
    assert not np.array_equal(a, grouped_split(groups, 0.3, seed=12))
    perm = np.random.default_rng(0).permutation(len(groups))
    shuffled = [groups[i] for i in perm]
    assert np.array_equal(grouped_split(shuffled, 0.3, seed=11), a[perm])
    train_groups = {g for g, t in zip(groups, a) if not t}
    test_groups = {g for g, t in zip(groups, a) if t}
    assert not train_groups & test_groups and train_groups | test_groups == set(groups)


def test_grouped_split_edge_sizes():
    two = grouped_split(["x", "x", "y"], 0.01, seed=0)
    assert two.sum() in (1, 2) and len({g for g, t in zip(["x", "x", "y"], two) if t}) == 1
    many = grouped_split(["a", "b", "c"], 0.99, seed=0)
    assert len({g for g, t in zip(["a", "b", "c"], many) if t}) == 2  # never all groups in test
    assert _raises(ValueError, grouped_split, ["only"] * 5, 0.5, 0)
    assert _raises(ValueError, grouped_split, ["a", "b"], 1.5, 0)


def test_temporal_split_boundaries_and_embargo():
    times = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    train, test = temporal_split(times, cutoff=7, embargo=2)
    assert train.tolist() == [t < 5 for t in times]
    assert test.tolist() == [t >= 7 for t in times]
    assert not (train & test).any()
    assert not train[4] and not test[4] and not train[5] and not test[5]  # 5 and 6 embargoed
    train0, test0 = temporal_split(times, cutoff=7)
    assert train0.tolist() == [t < 7 for t in times] and test0[6]
    assert _raises(ValueError, temporal_split, times, 7, -1)


def test_temporal_split_ties_and_unsorted_datetimes():
    times = np.array(["2024-01-03", "2024-01-01", "2024-01-05", "2024-01-05", "2024-01-04"], dtype="datetime64[D]")
    train, test = temporal_split(times, np.datetime64("2024-01-05"), np.timedelta64(1, "D"))
    assert test.tolist() == [False, False, True, True, False]
    assert train.tolist() == [True, True, False, False, False]  # 01-04 falls in the embargo


def test_check_leakage_clean_splits():
    times = np.arange(20)
    groups = [f"g{t // 2}" for t in times]
    train, test = temporal_split(times, 12, embargo=3)
    assert check_leakage(train, test, groups=groups, times=times, embargo=3) == []
    is_test = group_hash_split(groups, 0.4)
    assert check_leakage(~is_test, is_test, groups=groups) == []
    assert check_leakage(np.zeros(4, bool), np.ones(4, bool), groups=list("abcd"), times=np.arange(4)) == []


def test_check_leakage_reports_each_violation():
    groups = ["a", "a", "b", "b", "c"]
    times = np.array([1, 2, 3, 4, 5])
    train = np.array([True, False, True, True, False])
    test = np.array([False, True, False, False, True])
    assert check_leakage(train, test, groups=groups) == ["group_overlap"]
    assert check_leakage(train, test, times=times) == ["temporal_order"]
    assert check_leakage(train, test, groups=groups, times=times) == ["group_overlap", "temporal_order"]
    both = np.array([True, False, False, False, True])
    assert "row_overlap" in check_leakage(both, test)
    early = np.array([True, True, False, False, False])
    late = np.array([False, False, False, True, True])
    assert check_leakage(early, late, times=times, embargo=1) == []
    assert check_leakage(early, late, times=times, embargo=2) == ["embargo"]  # gap 4-2 = 2 <= 2
    assert check_leakage(early, late, times=times, embargo=0) == []


def test_check_leakage_temporal_tie_counts_as_violation():
    times = np.array([1, 3, 3, 4])
    train = np.array([True, True, False, False])
    test = np.array([False, False, True, True])
    assert check_leakage(train, test, times=times) == ["temporal_order"]
