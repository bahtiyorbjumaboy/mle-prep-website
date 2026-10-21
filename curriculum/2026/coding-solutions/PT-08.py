import math
import torch


def scaled_dot_product_attention(q, k, v, padding_mask=None, causal=False):
    """Compute attention for tensors shaped (..., query/key length, feature)."""
    scores = q @ k.transpose(-2, -1) / math.sqrt(q.shape[-1])
    allowed = torch.ones_like(scores, dtype=torch.bool)
    if padding_mask is not None:
        allowed &= padding_mask.to(dtype=torch.bool).unsqueeze(-2)
    if causal:
        allowed &= torch.ones(scores.shape[-2:], dtype=torch.bool, device=scores.device).tril()
    scores = scores.masked_fill(~allowed, -torch.inf)
    weights = torch.softmax(scores, dim=-1)
    weights = torch.where(allowed.any(dim=-1, keepdim=True), weights, torch.zeros_like(weights))
    return weights @ v, weights
