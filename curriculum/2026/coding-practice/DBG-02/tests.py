import numpy as np
import pandas as pd
import pytest

from solution import split_train_validation

N_EVENTS, POSITIVES, VALID_FRAC = 40, {3, 7, 11, 18, 22, 29, 33, 38}, 0.25
REPLAYED = [3, 7, 10, 15, 21, 30]  # event numbers that were ingested twice


def _dataset() -> tuple[pd.DataFrame, pd.Series, dict[str, int]]:
    """40 unique events (8 positive) plus 6 replays, scrambled, with a non-RangeIndex.

    `signal` equals the label, so any misalignment shows up as signal != y.
    """
    events = list(range(N_EVENTS)) + REPLAYED
    truth = {f"E{e:02d}": int(e in POSITIVES) for e in range(N_EVENTS)}
    rng = np.random.default_rng(12345)
    noise = rng.normal(size=len(events))
    frame = pd.DataFrame(
        {
            "event_id": [f"E{e:02d}" for e in events],
            "signal": [truth[f"E{e:02d}"] for e in events],
            "noise": noise,
        },
        index=[5000 + 37 * i for i in range(len(events))],
    )
    frame = frame.iloc[rng.permutation(len(frame))]
    labels = pd.Series(frame["signal"].to_numpy(), index=frame.index, name="churned")
    return frame.drop(columns="signal").assign(signal=frame["signal"]), labels.iloc[::-1], truth


def _check_alignment(X: pd.DataFrame, y: pd.Series, truth: dict[str, int]) -> None:
    assert y.index.equals(X.index), "each y must carry exactly the index of its X"
    assert [truth[e] for e in X["event_id"]] == y.tolist(), "labels detached from their rows"
    assert (X["signal"].to_numpy() == y.to_numpy()).all()


def test_labels_stay_attached_to_their_rows():
    features, labels, truth = _dataset()
    for seed in range(10):
        X_tr, X_va, y_tr, y_va = split_train_validation(features, labels, VALID_FRAC, seed)
        _check_alignment(X_tr, y_tr, truth)
        _check_alignment(X_va, y_va, truth)
        assert set(X_tr.index) | set(X_va.index) <= set(features.index), "original index labels"


def test_labels_are_matched_by_index_not_position():
    features, labels, _ = _dataset()
    aligned = labels.loc[features.index]
    for a, b in zip(
        split_train_validation(features, labels, VALID_FRAC, 3),
        split_train_validation(features, aligned, VALID_FRAC, 3),
    ):
        if isinstance(a, pd.DataFrame):
            pd.testing.assert_frame_equal(a, b)
        else:
            pd.testing.assert_series_equal(a, b)


def test_mismatched_label_index_raises():
    features, labels, _ = _dataset()
    with pytest.raises(ValueError):
        split_train_validation(features, labels.drop(labels.index[0]), VALID_FRAC, 0)
    with pytest.raises(ValueError):
        split_train_validation(features, labels.rename(index=lambda i: i + 1), VALID_FRAC, 0)


def test_each_event_lands_in_exactly_one_fold_once():
    features, labels, truth = _dataset()
    first_occurrence = set(features.index[~features["event_id"].duplicated(keep="first")])
    for seed in range(10):
        X_tr, X_va, _, _ = split_train_validation(features, labels, VALID_FRAC, seed)
        ids = list(X_tr["event_id"]) + list(X_va["event_id"])
        assert len(ids) == len(set(ids)) == len(truth), "every event exactly once overall"
        assert not set(X_tr["event_id"]) & set(X_va["event_id"]), "event in both folds"
        assert set(X_tr.index) | set(X_va.index) == first_occurrence, "keep first occurrence"


def test_conflicting_replays_raise():
    features, labels, _ = _dataset()
    replay = features.index[features["event_id"].duplicated(keep="first")][0]
    labels = labels.copy()
    labels.loc[replay] = 1 - labels.loc[replay]
    with pytest.raises(ValueError):
        split_train_validation(features, labels, VALID_FRAC, 0)


def test_validation_fold_is_stratified_for_every_seed():
    features, labels, _ = _dataset()
    n_pos, n_neg = len(POSITIVES), N_EVENTS - len(POSITIVES)
    for seed in range(20):
        X_tr, X_va, y_tr, y_va = split_train_validation(features, labels, VALID_FRAC, seed)
        assert int(y_va.sum()) == round(VALID_FRAC * n_pos), f"seed {seed}: validation positives"
        assert int((y_va == 0).sum()) == round(VALID_FRAC * n_neg), f"seed {seed}: negatives"
        assert int(y_tr.sum()) == n_pos - round(VALID_FRAC * n_pos)
        assert len(X_va) == len(y_va) and len(X_tr) == len(y_tr)


def test_split_is_deterministic_and_seed_dependent():
    features, labels, _ = _dataset()
    first = split_train_validation(features, labels, VALID_FRAC, 7)
    again = split_train_validation(features, labels, VALID_FRAC, 7)
    for a, b in zip(first, again):
        pd.testing.assert_index_equal(a.index, b.index)
    validation_sets = {
        frozenset(split_train_validation(features, labels, VALID_FRAC, s)[1]["event_id"])
        for s in range(5)
    }
    assert len(validation_sets) > 1, "different seeds should give different splits"


def test_inputs_are_not_mutated():
    features, labels, _ = _dataset()
    f_copy, l_copy = features.copy(), labels.copy()
    split_train_validation(features, labels, VALID_FRAC, 0)
    pd.testing.assert_frame_equal(features, f_copy)
    pd.testing.assert_series_equal(labels, l_copy)
