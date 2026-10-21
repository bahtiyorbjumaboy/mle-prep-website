import json
from collections import Counter

import numpy as np

# Incident: the churn model (`m12`, trained with transformer `v7`) reproduces its offline
# AUC exactly, but the online service's scores are shifted: replaying yesterday's requests
# through serving gives different probabilities than the offline batch job. A newer
# transformer `v8` was published to the registry last week for an upcoming model.
#
# Canonical prompt: offline predictions match expected metrics, but a serving path produces
# shifted scores. Given training preprocessing, serialized transformer state, model
# weights, and online feature code, localize one preprocessing mismatch, one stale-version
# mismatch, and one dtype/device/numerical discrepancy. Add parity tests that catch the
# first divergence.
# Follow-ups: unknown categories; model/index coupling; feature freshness; rollback.

NUMERIC = ("account_age_s", "income")

# ---- Training side (offline). Trusted: this is the path that produced the metrics. ----


def fit_transformer(rows: list[dict], version: str) -> dict:
    """Fits the preprocessing state that training serializes into the registry.

    Features: `account_age_s` standardized; `income` as `log1p` then standardized
    (population std); `country` one-hot in `vocab` order (most frequent first, ties by
    name). An unknown country encodes as an all-zero one-hot block.
    """
    age = np.array([r["account_age_s"] for r in rows], dtype=np.float64)
    log_income = np.log1p(np.array([r["income"] for r in rows], dtype=np.float64))
    counts = Counter(r["country"] for r in rows)
    return {
        "version": version,
        "mean": {"account_age_s": float(age.mean()), "income": float(log_income.mean())},
        "std": {"account_age_s": float(age.std()), "income": float(log_income.std())},
        "vocab": [c for c, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))],
    }


def transform_rows(rows: list[dict], state: dict) -> np.ndarray:
    """`(n, 2 + len(vocab))` float64 feature matrix: `[age_z, log_income_z, one-hot...]`."""
    mean, std = state["mean"], state["std"]
    age = np.array([r["account_age_s"] for r in rows], dtype=np.float64)
    log_income = np.log1p(np.array([r["income"] for r in rows], dtype=np.float64))
    index = {country: i for i, country in enumerate(state["vocab"])}
    onehot = np.zeros((len(rows), len(index)))
    for i, row in enumerate(rows):
        if row["country"] in index:
            onehot[i, index[row["country"]]] = 1.0
    numeric = np.column_stack(
        [
            (age - mean["account_age_s"]) / std["account_age_s"],
            (log_income - mean["income"]) / std["income"],
        ]
    )
    return np.hstack([numeric, onehot])


def sigmoid(z: np.ndarray) -> np.ndarray:
    e = np.exp(-np.abs(z))
    return np.where(z >= 0, 1.0 / (1.0 + e), e / (1.0 + e))


def predict_offline(rows: list[dict], state: dict, model: dict) -> np.ndarray:
    weights = np.asarray(model["weights"], dtype=np.float64)
    return sigmoid(transform_rows(rows, state) @ weights + model["bias"])


# ---- Serving side (online). ----


class OnlinePredictor:
    """Scores one request at a time in the online service.

    Args:
        registry: `{transformer_version: serialized state (JSON)}`; several versions coexist.
        model: `{"model_version", "transformer_version", "weights", "bias"}`, where
            `transformer_version` names the state the weights were trained against.

    Contract:
    - Serving uses exactly the transformer state the model was trained with. If that version
      is missing from the registry, or the stored state's own `"version"` disagrees, the
      constructor raises `ValueError` instead of guessing.
    - For any request, `features(request)` equals `transform_rows([request], state)[0]` and
      `predict(request)` equals `predict_offline([request], state, model)[0]`, both within
      `1e-9` absolute. Requests are not mutated.
    """

    def __init__(self, registry: dict[str, str], model: dict):
        self.state = json.loads(registry[max(registry)])
        self.model = model
        self.weights = np.asarray(model["weights"], dtype=np.float64)
        self.vocab = sorted(self.state["vocab"])

    def features(self, request: dict) -> np.ndarray:
        raw = np.array([request["account_age_s"], request["income"]], dtype=np.float32)
        mean, std = self.state["mean"], self.state["std"]
        age_z = (raw[0] - mean["account_age_s"]) / std["account_age_s"]
        income_z = (np.log1p(raw[1]) - mean["income"]) / std["income"]
        onehot = [1.0 if request["country"] == country else 0.0 for country in self.vocab]
        return np.array([age_z, income_z, *onehot], dtype=np.float64)

    def predict(self, request: dict) -> float:
        return float(sigmoid(self.features(request) @ self.weights + self.model["bias"]))
