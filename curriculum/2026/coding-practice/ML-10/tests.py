import math

import numpy as np

from solution import entropy, gini, information_gain, weighted_child_impurity


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _strict(fn, *args, **kwargs):
    with np.errstate(divide="raise", invalid="raise"):
        return fn(*args, **kwargs)


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("entropy", "gini", "weighted_child_impurity", "information_gain"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_pure_node_is_zero():
    for labels in (np.array([3, 3, 3]), np.array(["a"]), np.array([-1, -1])):
        assert entropy(labels=labels) == 0.0 and gini(labels=labels) == 0.0
    assert _strict(entropy, probs=np.array([0.0, 1.0, 0.0])) == 0.0
    assert _strict(gini, probs=np.array([1.0, 0.0])) == 0.0


def test_balanced_binary_and_uniform_multiclass():
    assert math.isclose(entropy(labels=np.array([0, 1, 0, 1])), 1.0)
    assert math.isclose(entropy(labels=np.array([0, 1, 0, 1]), base=np.e), math.log(2))
    assert math.isclose(gini(labels=np.array([0, 1, 0, 1])), 0.5)
    four = np.array([0, 1, 2, 3, 3, 2, 1, 0])
    assert math.isclose(entropy(labels=four), 2.0) and math.isclose(gini(labels=four), 0.75)


def test_hand_computed_imbalanced_and_probability_input():
    labels = np.array([0, 0, 0, 1])
    h = -(0.75 * math.log2(0.75) + 0.25 * math.log2(0.25))
    assert math.isclose(entropy(labels=labels), h)
    assert math.isclose(gini(labels=labels), 1 - 0.75 ** 2 - 0.25 ** 2)
    assert math.isclose(entropy(probs=np.array([0.75, 0.25])), h)
    p = np.array([0.5, 0.0, 0.25, 0.25])
    assert math.isclose(_strict(entropy, probs=p), 1.5) and math.isclose(gini(probs=p), 0.625)


def test_zero_log_zero_does_not_produce_nan_or_warnings():
    p = np.array([0.0, 0.0, 1e-300, 1.0 - 1e-300])
    out = _strict(entropy, probs=p)
    assert math.isfinite(out) and 0.0 <= out < 1e-290
    # 1.0 + 1e-20 == 1.0 in float64, so this is a valid distribution; log(p + eps) hacks
    # are off by ~40% here (true H = 1e-20 * log2(1e20) bits).
    tiny = _strict(entropy, probs=np.array([1e-20, 1.0]))
    assert math.isclose(tiny, 1e-20 * math.log2(1e20), rel_tol=1e-9)


def test_invariant_to_label_renaming_and_order():
    a = np.array([0, 0, 1, 2, 2, 2])
    renamed = np.array(["z", "z", "x", "y", "y", "y"])
    shifted = np.array([-7, -7, 1000, 5, 5, 5])
    for f in (entropy, gini):
        base = f(labels=a)
        assert math.isclose(f(labels=renamed), base) and math.isclose(f(labels=shifted), base)
        assert math.isclose(f(labels=a[::-1]), base)


def test_sample_weights_equal_duplication():
    labels = np.array([0, 1, 1, 2])
    w = np.array([2.0, 1.0, 0.0, 3.0])
    duplicated = np.array([0, 0, 1, 2, 2, 2])
    for f in (entropy, gini):
        assert math.isclose(f(labels=labels, weights=w), f(labels=duplicated))


def test_information_gain_pure_children_equals_parent_impurity():
    labels = np.array([0, 0, 1, 1, 1, 1])
    mask = np.array([True, True, False, False, False, False])
    assert math.isclose(information_gain(labels, mask), entropy(labels=labels))
    assert math.isclose(information_gain(labels, mask, "gini"), gini(labels=labels))
    assert weighted_child_impurity(labels, mask) == 0.0


def test_children_are_weighted_by_mass_not_averaged():
    labels = np.array([0, 1, 0, 0, 0, 0, 1, 1])
    mask = np.array([True, True, False, False, False, False, False, False])
    # left: [0, 1] (H=1, size 2); right: [0, 0, 0, 0, 1, 1] (size 6)
    h_right = -(4 / 6 * math.log2(4 / 6) + 2 / 6 * math.log2(2 / 6))
    child = 2 / 8 * 1.0 + 6 / 8 * h_right
    assert math.isclose(weighted_child_impurity(labels, mask), child)
    assert math.isclose(information_gain(labels, mask), entropy(labels=labels) - child)
    assert not math.isclose(information_gain(labels, mask), entropy(labels=labels) - (1.0 + h_right) / 2)
    g_child = 2 / 8 * 0.5 + 6 / 8 * (1 - (4 / 6) ** 2 - (2 / 6) ** 2)
    assert math.isclose(weighted_child_impurity(labels, mask, "gini"), g_child)


def test_weighted_split_uses_child_weight_mass():
    labels = np.array([0, 1, 1, 0])
    mask = np.array([True, True, False, False])
    w = np.array([3.0, 1.0, 1.0, 1.0])
    dup_labels = np.array([0, 0, 0, 1, 1, 0])
    dup_mask = np.array([True, True, True, True, False, False])
    assert math.isclose(information_gain(labels, mask, weights=w), information_gain(dup_labels, dup_mask))
    assert math.isclose(
        weighted_child_impurity(labels, mask, "gini", weights=w), weighted_child_impurity(dup_labels, dup_mask, "gini")
    )


def test_multiclass_gain_and_base():
    labels = np.array(["a", "b", "c", "a", "b", "c"])
    mask = np.array([True, True, False, False, False, False])
    bits = information_gain(labels, mask)
    nats = information_gain(labels, mask, base=np.e)
    assert math.isclose(nats, bits * math.log(2))
    assert 0 < bits < entropy(labels=labels)


def test_useless_split_has_zero_gain():
    labels = np.array([0, 1, 0, 1])
    mask = np.array([True, True, False, False])
    assert math.isclose(information_gain(labels, mask), 0.0, abs_tol=1e-12)


def test_empty_child_and_input_validation():
    labels = np.array([0, 1, 1])
    assert _raises(ValueError, information_gain, labels, np.array([False, False, False]))
    assert _raises(ValueError, information_gain, labels, np.array([True, True, True]))
    assert _raises(ValueError, information_gain, labels, np.array([True, False, False]), weights=np.array([0.0, 1.0, 1.0]))
    assert _raises(ValueError, information_gain, labels, np.array([1, 0, 0]))
    assert _raises(ValueError, information_gain, labels, np.array([True, False]))
    assert _raises(ValueError, information_gain, labels, np.array([True, False, False]), "mse")
    assert _raises(ValueError, entropy)
    assert _raises(ValueError, entropy, labels=labels, probs=np.array([0.5, 0.5]))
    assert _raises(ValueError, entropy, probs=np.array([0.5, 0.6]))
    assert _raises(ValueError, gini, probs=np.array([1.5, -0.5]))
    assert _raises(ValueError, entropy, labels=np.array([], dtype=int))
    assert _raises(ValueError, gini, labels=labels, weights=np.array([1.0, -1.0, 1.0]))
