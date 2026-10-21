import numpy as np

# Incident: the offline report says precision 0.91 / recall 0.88 for the fraud classifier;
# after launch, analysts measure precision around 0.4. The metrics also change when the
# evaluation batch size or the seed changes.
#
# Canonical prompt: an evaluation function applies a 0.5 threshold to logits, averages
# per-batch precision, uses the wrong recall denominator, and evaluates on an oversampled
# validation population. Fix it and write hand-computed tests.
# Follow-up: which bugs inflate vs deflate metrics?


def make_batches(
    labels: np.ndarray, batch_size: int, balance: bool = False, seed: int = 0
) -> list[np.ndarray]:
    """Index batches over a dataset; shared with the training loader.

    With `balance=True` the positives are resampled with replacement until they match the
    number of negatives (training-time oversampling), and the order is shuffled.
    """
    idx = np.arange(len(labels))
    if balance:
        rng = np.random.default_rng(seed)
        pos, neg = idx[labels == 1], idx[labels == 0]
        idx = rng.permutation(np.concatenate([neg, rng.choice(pos, size=len(neg), replace=True)]))
    return [idx[i : i + batch_size] for i in range(0, len(idx), batch_size)]


def evaluate(
    logits: np.ndarray,
    labels: np.ndarray,
    threshold: float = 0.5,
    batch_size: int = 256,
    seed: int = 0,
) -> dict[str, float]:
    """Binary-classification metrics for a validation set.

    Contract:
    - `logits` are raw model outputs (pre-sigmoid); `labels` are 0/1.
    - An example is predicted positive iff `sigmoid(logit) >= threshold` (0 < threshold < 1).
    - The population is the validation set as given: every example exactly once, at its
      natural class balance.
    - `precision = TP / (TP + FP)`, `recall = TP / (TP + FN)`, `f1 = 2PR / (P + R)`, each
      computed from counts over the whole population; any 0/0 is reported as 0.0.
    - `batch_size` only bounds memory and `seed` must not matter: neither may change a result.

    Returns:
        `precision`, `recall`, `f1`, `tp`, `fp`, `fn`, `n` (examples evaluated), and
        `positive_rate` (fraction of evaluated examples with label 1).
    """
    logits = np.asarray(logits, dtype=float)
    labels = np.asarray(labels).astype(int)

    tp = fp = fn = n = n_pos = 0
    batch_precisions = []
    for batch in make_batches(labels, batch_size, balance=True, seed=seed):
        y = labels[batch] == 1
        pred = logits[batch] >= threshold
        b_tp, b_fp, b_fn = int(np.sum(pred & y)), int(np.sum(pred & ~y)), int(np.sum(~pred & y))
        batch_precisions.append(b_tp / (b_tp + b_fp) if b_tp + b_fp else 0.0)
        tp, fp, fn = tp + b_tp, fp + b_fp, fn + b_fn
        n, n_pos = n + len(batch), n_pos + int(y.sum())

    precision = float(np.mean(batch_precisions))
    recall = tp / (tp + fp) if tp + fp else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "n": n,
        "positive_rate": n_pos / n if n else 0.0,
    }
