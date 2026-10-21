import torch


def batched_scores(q: torch.Tensor, k: torch.Tensor) -> torch.Tensor:
    # (B, Tq, D) @ (B, D, Tk) -> (B, Tq, Tk); k.T / transpose(0, 1) would swap the wrong axes.
    return q @ k.transpose(-2, -1)


def bilinear_scores(x: torch.Tensor, w: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    # (B, N, D), (D, E), (B, M, E) -> (B, N, M)
    return torch.einsum("bnd,de,bme->bnm", x, w, y)


def embedding_lookup(table: torch.Tensor, ids: torch.Tensor) -> torch.Tensor:
    if ids.numel() and (int(ids.min()) < 0 or int(ids.max()) >= table.shape[0]):
        raise ValueError(f"ids must lie in [0, {table.shape[0]})")
    # Advanced indexing keeps the ids' shape and appends D; backward scatter-adds
    # into table rows, so repeated ids accumulate gradient.
    return table[ids]  # (*S, D)


def masked_mean_pool(x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    m = mask.unsqueeze(-1).to(x.dtype)  # (B, T, 1): broadcasts over D, not over B or T
    summed = torch.where(mask.unsqueeze(-1), x, torch.zeros_like(x)).sum(dim=1)  # (B, D)
    counts = m.sum(dim=1).clamp_min(1.0)  # (B, 1); empty rows divide 0 by 1
    return summed / counts


def causal_mask(t: int, device: torch.device | str | None = None) -> torch.Tensor:
    return torch.ones(t, t, dtype=torch.bool, device=device).tril()  # (T, T), True on/below diagonal


def causal_softmax(scores: torch.Tensor) -> torch.Tensor:
    allowed = causal_mask(scores.shape[-1], device=scores.device)
    # Mask BEFORE softmax so masked keys get exactly 0 and allowed weights renormalise.
    # The diagonal is always allowed, so no row is fully masked.
    return torch.softmax(scores.masked_fill(~allowed, float("-inf")), dim=-1)


def pairwise_sq_dists_buggy(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return ((a - b) ** 2).sum(dim=-1)


# Diagnosis: (B, D) - (K, D) broadcasts row-against-row, not all pairs.
# - B != K (both > 1): raises a broadcast error, so the bug is at least loud.
# - B == K: runs silently and returns the (B,) distances ||a_i - b_i||^2 (diagonal only).
# - B == 1 or K == 1: broadcasting happens to give all pairs, but as a 1-D (K,) / (B,)
#   vector instead of (1, K) / (B, 1), so downstream code indexing [i, j] breaks.
# Fix: insert singleton axes so the pair grid is explicit: (B, 1, D) - (1, K, D) -> (B, K, D).


def pairwise_sq_dists(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    diff = a.unsqueeze(1) - b.unsqueeze(0)  # (B, K, D)
    return (diff ** 2).sum(dim=-1)  # (B, K)
