import json
import math

import numpy as np

from solution import OnlinePredictor, fit_transformer, predict_offline, transform_rows

TOL = 1e-9
GOLDEN = {"account_age_s": 123_456_789, "income": 52_000.0, "country": "US"}  # "US" sits at a different one-hot index in sorted order


def _rows(seed, countries, probs, age_range, income_scale, n=400):
    rng = np.random.default_rng(seed)
    return [
        {
            "account_age_s": int(age),
            "income": float(round(income, 2)),
            "country": str(country),
        }
        for age, income, country in zip(
            rng.integers(*age_range, size=n),
            rng.gamma(3.0, income_scale, size=n),
            rng.choice(countries, size=n, p=probs),
        )
    ]


COUNTRIES = ["US", "DE", "FR", "BR", "JP"]
ROWS_V7 = _rows(7, COUNTRIES, [0.4, 0.25, 0.15, 0.12, 0.08], (1_000_000, 250_000_000), 15_000.0)
ROWS_V8 = _rows(8, COUNTRIES, [0.3, 0.08, 0.12, 0.35, 0.15], (50_000_000, 400_000_000), 30_000.0)
MODEL_V7 = {"model_version": "m12", "transformer_version": "v7",
            "weights": [0.9, -1.3, 0.4, -0.6, 1.1, -0.2, 0.7], "bias": -0.3}
MODEL_V8 = {"model_version": "m13", "transformer_version": "v8",
            "weights": [-0.5, 0.8, 0.3, 0.2, -0.9, 1.4, -0.1], "bias": 0.2}


def _registry():
    return {"v7": json.dumps(fit_transformer(ROWS_V7, "v7")), "v8": json.dumps(fit_transformer(ROWS_V8, "v8"))}


# ---- Independent oracle of the documented training-side semantics (pure Python). ----

def _oracle_state(rows):
    def mean_std(values):
        mean = math.fsum(values) / len(values)
        return mean, math.sqrt(math.fsum((v - mean) ** 2 for v in values) / len(values))

    age = mean_std([float(r["account_age_s"]) for r in rows])
    income = mean_std([math.log1p(r["income"]) for r in rows])
    counts = {}
    for r in rows:
        counts[r["country"]] = counts.get(r["country"], 0) + 1
    vocab = sorted(counts, key=lambda c: (-counts[c], c))
    return {"age": age, "income": income, "vocab": vocab}


def _oracle_features(request, oracle):
    (am, asd), (im, isd) = oracle["age"], oracle["income"]
    return [(request["account_age_s"] - am) / asd, (math.log1p(request["income"]) - im) / isd] + [
        1.0 if request["country"] == c else 0.0 for c in oracle["vocab"]
    ]


def _oracle_score(request, oracle, model):
    z = math.fsum(w * f for w, f in zip(model["weights"], _oracle_features(request, oracle))) + model["bias"]
    return 1.0 / (1.0 + math.exp(-z))


def _assert_parity(actual, expected, vocab, what):
    names = ["account_age_z", "log_income_z"] + [f"country={c}" for c in vocab]
    actual, expected = np.asarray(actual, dtype=np.float64), np.asarray(expected, dtype=np.float64)
    assert actual.shape == expected.shape, f"{what}: shape {actual.shape} != {expected.shape}"
    diff = np.abs(actual - expected)
    if (diff > TOL).any():
        i = int(np.argmax(diff > TOL))
        raise AssertionError(
            f"{what}: first divergence at {names[i]}: serving {actual[i]!r} vs offline {expected[i]!r}"
        )


def _raises_value_error(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def test_training_side_matches_the_independent_oracle():
    oracle = _oracle_state(ROWS_V7)
    state = fit_transformer(ROWS_V7, "v7")
    assert state["vocab"] == oracle["vocab"] == ["US", "DE", "FR", "BR", "JP"]
    assert math.isclose(state["mean"]["account_age_s"], oracle["age"][0], rel_tol=1e-12)
    assert math.isclose(state["std"]["income"], oracle["income"][1], rel_tol=1e-12)
    requests = ROWS_V7[:20] + [GOLDEN]
    _assert_parity(transform_rows(requests, state), [_oracle_features(r, oracle) for r in requests], oracle["vocab"], "offline")
    expected = [_oracle_score(r, oracle, MODEL_V7) for r in requests]
    assert np.allclose(predict_offline(requests, state, MODEL_V7), expected, atol=TOL, rtol=0)


def test_golden_request_intermediate_features_match_offline():
    oracle = _oracle_state(ROWS_V7)
    serving = OnlinePredictor(_registry(), MODEL_V7)
    _assert_parity(serving.features(GOLDEN), _oracle_features(GOLDEN, oracle), oracle["vocab"], "golden features")


def test_golden_request_prediction_matches_offline():
    oracle = _oracle_state(ROWS_V7)
    serving = OnlinePredictor(_registry(), MODEL_V7)
    expected = _oracle_score(GOLDEN, oracle, MODEL_V7)
    assert abs(serving.predict(GOLDEN) - expected) <= TOL, (serving.predict(GOLDEN), expected)


def test_serving_uses_the_transformer_the_model_was_trained_with():
    # The registry also holds the newer v8; model m12 was trained against v7.
    state_v7 = fit_transformer(ROWS_V7, "v7")
    serving = OnlinePredictor(_registry(), MODEL_V7)
    probe = {"account_age_s": 10_000_000, "income": 30_000.0, "country": "DE"}
    _assert_parity(serving.features(probe), transform_rows([probe], state_v7)[0], state_v7["vocab"], "v7 features")


def test_missing_or_mislabeled_transformer_is_rejected():
    registry = _registry()
    assert _raises_value_error(lambda: OnlinePredictor({"v8": registry["v8"]}, MODEL_V7)), "missing v7"
    mislabeled = {"v7": registry["v8"], "v8": registry["v8"]}
    assert _raises_value_error(lambda: OnlinePredictor(mislabeled, MODEL_V7)), "v7 slot holds v8"


def test_replayed_traffic_matches_offline_batch_scoring():
    rng = np.random.default_rng(11)
    requests = [
        {"account_age_s": int(a), "income": float(i), "country": str(c)}
        for a, i, c in zip(
            rng.integers(0, 600_000_000, size=300),
            rng.gamma(2.0, 40_000.0, size=300),
            rng.choice(COUNTRIES + ["ZZ"], size=300),
        )
    ] + [
        {"account_age_s": 0, "income": 0.0, "country": "ZZ"},
        {"account_age_s": 5_000_000_000, "income": 10_000_000.0, "country": "JP"},
        {"account_age_s": 123_456_791, "income": 0.01, "country": "US"},
    ]
    state = fit_transformer(ROWS_V7, "v7")
    serving = OnlinePredictor(_registry(), MODEL_V7)
    offline_features = transform_rows(requests, state)
    offline_scores = predict_offline(requests, state, MODEL_V7)
    for i, request in enumerate(requests):
        _assert_parity(serving.features(request), offline_features[i], state["vocab"], f"request {i}")
        assert abs(serving.predict(request) - offline_scores[i]) <= TOL, f"request {i} score"


def test_parity_holds_for_a_newer_model_and_transformer():
    oracle = _oracle_state(ROWS_V8)
    serving = OnlinePredictor(_registry(), MODEL_V8)
    _assert_parity(serving.features(GOLDEN), _oracle_features(GOLDEN, oracle), oracle["vocab"], "v8 features")
    assert abs(serving.predict(GOLDEN) - _oracle_score(GOLDEN, oracle, MODEL_V8)) <= TOL


def test_unknown_country_and_request_immutability():
    serving = OnlinePredictor(_registry(), MODEL_V7)
    request = {"account_age_s": 99_000_000, "income": 41_000.0, "country": "ZZ"}
    snapshot = dict(request)
    features = serving.features(request)
    assert list(features[2:]) == [0.0] * 5
    serving.predict(request)
    assert request == snapshot
