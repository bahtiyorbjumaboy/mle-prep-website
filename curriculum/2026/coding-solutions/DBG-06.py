import numpy as np

# Repair of the DBG-06 starter. The defects and their fixes:
# 1. `logits >= 0.5` compared raw logits with a probability threshold (it equals
#    sigmoid(logit) >= 0.62). Fix: compare logits with logit(threshold) = log(t / (1 - t)),
#    which is exact and needs no exp.
# 2. Averaging per-batch precision weights every batch equally, so the result depends on
#    batch size. Fix: accumulate TP/FP/FN over all batches, then divide once.
# 3. Recall used TP + FP (the precision denominator). Fix: TP + FN.
# 4. The validation set was oversampled with the training loader's `balance=True`, which
#    inflates the positive rate and precision and can drop positives entirely. Fix: evaluate
#    the natural population (`balance=False`). Deduplicating the oversampled indices would
#    not recover it, because resampling with replacement can omit some positives.


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
    for batch in make_batches(labels, batch_size, balance=False):
        y = labels[batch] == 1
        pred = logits[batch] >= np.log(threshold / (1.0 - threshold))
        b_tp, b_fp, b_fn = int(np.sum(pred & y)), int(np.sum(pred & ~y)), int(np.sum(~pred & y))
        tp, fp, fn = tp + b_tp, fp + b_fp, fn + b_fn
        n, n_pos = n + len(batch), n_pos + int(y.sum())

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
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
