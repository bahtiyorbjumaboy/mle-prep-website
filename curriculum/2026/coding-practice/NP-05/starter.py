import numpy as np


def pad_sequences(sequences: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Right-pad variable-length sequences into `(B, T, d)` plus a `(B, T)` mask.

    Args:
        sequences: `B >= 1` arrays of shape `(L_i, d)` with `L_i >= 0` and a shared `d`.

    Returns:
        `(padded, mask)`: float64 `(B, T, d)` with `T = max L_i` (0 if all are empty),
        padding filled with 0.0; boolean `(B, T)` with `mask[i, t] = t < L_i`.

    Raises:
        ValueError: if `sequences` is empty, an element is not 2-D, or `d` differs.
    """
    raise NotImplementedError("TODO: implement NP-05")


def masked_mean_pool(padded: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Mean over real positions: `(B, T, d)`, `(B, T)` -> `(B, d)`.

    `mask` may be any boolean pattern (right- or left-padded). Values at padded
    positions are arbitrary (they may be NaN or inf) and must not affect any pooled
    output; this holds for all three pooling functions. A row with no real positions
    pools to zeros (never NaN). No Python loops over B or T.
    """
    raise NotImplementedError("TODO: implement NP-05")


def last_n_mean_pool(padded: np.ndarray, mask: np.ndarray, n: int = 5) -> np.ndarray:
    """Mean over each row's last `min(n, #real)` real positions -> `(B, d)`.

    "Last" means the real positions with the largest time indices, so this must work
    for left-padded masks too. Rows with no real positions pool to zeros.
    No Python loops over B or T.

    Raises:
        ValueError: if `n < 1`.
    """
    raise NotImplementedError("TODO: implement NP-05")


def masked_max_pool(padded: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Elementwise max over real positions -> `(B, d)`; padding must never win.

    Rows with no real positions pool to zeros. No Python loops over B or T.
    """
    raise NotImplementedError("TODO: implement NP-05")


def pad_and_pool(
    sequences: list[np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Canonical prompt: given variable-length sequences of d-dimensional vectors,
    construct a padded `(B,T,d)` array and `(B,T)` mask, then compute masked mean and
    mean over the last five real positions.

    Returns:
        `(padded, mask, masked_mean, last5_mean)` using the functions above.
    """
    raise NotImplementedError("TODO: implement NP-05")
