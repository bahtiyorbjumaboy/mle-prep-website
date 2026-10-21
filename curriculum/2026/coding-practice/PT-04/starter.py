import torch

# Canonical prompt: implement batched matmul, einsum, embedding lookup, masked pooling,
# and a causal mask; then diagnose a pairwise-distance function that silently broadcasts
# incorrectly for particular shapes.
#
# Annotate shapes as you go. Tests use unequal sizes (and the B == K coincidence), so
# code that only works when dimensions happen to match will fail.


def batched_scores(q: torch.Tensor, k: torch.Tensor) -> torch.Tensor:
    """Batched matmul: `q` `(B, Tq, D)`, `k` `(B, Tk, D)` -> `q_i . k_j` scores `(B, Tq, Tk)`."""
    raise NotImplementedError("TODO: implement PT-04")


def bilinear_scores(x: torch.Tensor, w: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """With `torch.einsum`: `x` `(B, N, D)`, `w` `(D, E)`, `y` `(B, M, E)` -> `x W y^T` `(B, N, M)`."""
    raise NotImplementedError("TODO: implement PT-04")


def embedding_lookup(table: torch.Tensor, ids: torch.Tensor) -> torch.Tensor:
    """`table` `(V, D)`, int64 `ids` of any shape `S` -> `(*S, D)`, differentiable w.r.t. `table`.

    Do not use `nn.Embedding` / `F.embedding`. Ids outside `[0, V)` raise `ValueError`.
    """
    raise NotImplementedError("TODO: implement PT-04")


def masked_mean_pool(x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """`x` `(B, T, D)`, bool `mask` `(B, T)` (True = real token) -> mean of real tokens `(B, D)`.

    Padded values must not influence the result (even if huge). A row with no real
    tokens pools to zeros.
    """
    raise NotImplementedError("TODO: implement PT-04")


def causal_mask(t: int, device: torch.device | str | None = None) -> torch.Tensor:
    """Bool `(t, t)` mask where `[i, j]` is True iff query `i` may attend to key `j` (`j <= i`)."""
    raise NotImplementedError("TODO: implement PT-04")


def causal_softmax(scores: torch.Tensor) -> torch.Tensor:
    """Softmax over the last axis of `scores` `(..., T, T)` with future keys masked out.

    Masked weights are exactly 0 and every row sums to 1.
    """
    raise NotImplementedError("TODO: implement PT-04")


def pairwise_sq_dists_buggy(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Intended: `a` `(B, D)`, `b` `(K, D)` -> squared distances `(B, K)`.

    Diagnose (as a comment): for which shapes does this raise, for which does it run but
    return the wrong thing, and why? Do not edit this function; fix it below.
    """
    return ((a - b) ** 2).sum(dim=-1)


def pairwise_sq_dists(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Correct version: `(B, D)`, `(K, D)` -> `(B, K)` with `[i, j] = ||a_i - b_j||^2 >= 0`."""
    raise NotImplementedError("TODO: implement PT-04")
