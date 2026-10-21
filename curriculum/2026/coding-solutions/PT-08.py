import math

import torch


def scaled_dot_product_attention(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    padding_mask: torch.Tensor | None = None,
    causal: bool = False,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Attention for q `(B, ..., Tq, d_k)`, k `(B, ..., Tk, d_k)`, v `(B, ..., Tk, d_v)`."""
    if q.shape[-1] != k.shape[-1] or k.shape[-2] != v.shape[-2]:
        raise ValueError("need q/k feature sizes to match and k/v lengths to match")
    scores = q @ k.transpose(-2, -1) / math.sqrt(q.shape[-1])  # (B, ..., Tq, Tk)
    allowed = torch.ones_like(scores, dtype=torch.bool)
    if padding_mask is not None:
        if padding_mask.shape != (scores.shape[0], scores.shape[-1]):
            raise ValueError("padding_mask must have shape (B, Tk)")
        # (B, Tk) -> (B, 1, ..., 1, Tk): align with the batch axis, broadcast over heads and queries.
        # A bare unsqueeze(-2) gives (B, 1, Tk), which lines up B against the head axis.
        view = (scores.shape[0],) + (1,) * (scores.dim() - 2) + (scores.shape[-1],)
        allowed &= padding_mask.to(dtype=torch.bool).reshape(view)
    if causal:
        # Query i may attend key j iff j <= i (top-left aligned, as in F.scaled_dot_product_attention).
        allowed &= torch.ones(scores.shape[-2:], dtype=torch.bool, device=scores.device).tril()
    scores = scores.masked_fill(~allowed, -torch.inf)  # mask BEFORE softmax
    weights = torch.softmax(scores, dim=-1)  # over keys
    # All-masked rows would be softmax(-inf, ..., -inf) = NaN; define them as all-zero weights.
    weights = torch.where(allowed.any(dim=-1, keepdim=True), weights, torch.zeros_like(weights))
    return weights @ v, weights  # (B, ..., Tq, d_v), (B, ..., Tq, Tk)
