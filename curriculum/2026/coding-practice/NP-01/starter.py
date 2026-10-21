import numpy as np


def array_operations(
    x: np.ndarray,
    weights: np.ndarray | None = None,
    mask: np.ndarray | None = None,
) -> dict[str, np.ndarray]:
    """Row normalization, column standardization, masked mean, and weighted row mean.

    Canonical prompt: given arrays of shapes `(B,D)`, `(D,)`, `(B,1)`, and boolean
    masks, predict the output shape or error for additions, reductions, matmul,
    masking, and normalization expressions. Then implement the four operations below.

    Warm-up (answer on paper first, then check in a REPL) with x `(3, 4)`,
    w `(4,)`, c `(3, 1)`, m `(3, 4)` bool:
    `x + w`, `x + c`, `x + x.sum(axis=1)`, `x + x.sum(axis=1, keepdims=True)`,
    `x @ w`, `w @ x`, `x.T @ c`, `x[m]`, `x / x.sum(axis=0)`, `w + c`.

    Contract (vectorized; no Python loops over B or D; inputs are never modified):

    Args:
        x: Real array of shape `(B, D)`, `B >= 1`, `D >= 1`; integer input is allowed.
        weights: Non-negative per-column weights of shape `(D,)` with a positive sum.
            `None` means uniform weights.
        mask: Mask of shape `(B, D)`; `True` marks entries to include. A 0/1 integer
            mask means the same as the equivalent boolean mask. `None` means all True.

    Returns:
        A dict of float64 arrays:
        - `"row_normalized"` `(B, D)`: each row divided by its L2 norm; an all-zero
          row stays all zeros (no NaN).
        - `"col_standardized"` `(B, D)`: `(x - column mean) / column std`, using the
          population std (`ddof=0`). A column whose entries are all equal maps to 0.
        - `"masked_mean"` `(B,)`: mean of each row's masked entries; NaN for a row with
          no masked entries.
        - `"weighted_row_mean"` `(B,)`: `sum_j w_j * x[i, j] / sum_j w_j`.

    Raises:
        ValueError: if `x` is not 2-D, `weights` is not shape `(D,)`, has a negative
            entry or sums to zero, or `mask` is not shape `(B, D)`.
    """
    raise NotImplementedError("TODO: implement NP-01")
