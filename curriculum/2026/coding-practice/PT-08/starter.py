import math

import torch

# Canonical prompt: given `Q, K, V` tensors, implement scaled dot-product attention with
# padding and causal masks. Support batched multi-head shapes, apply masks before
# softmax, and return both outputs and attention weights.
# Follow-ups: all-masked row policy; different query/key lengths; flash attention.
# Required mastery tests: causal future weights are zero; padding weights are zero;
# rows sum to one when at least one key is valid.


def scaled_dot_product_attention(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    padding_mask: torch.Tensor | None = None,
    causal: bool = False,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return `(output, weights)`.

    Shapes: `q` `(B, ..., Tq, d_k)`, `k` `(B, ..., Tk, d_k)`, `v` `(B, ..., Tk, d_v)`,
    where `...` is zero or more head axes (e.g. `(B, H, T, d)`). `Tq`, `Tk`, `d_k`, `d_v`
    may all differ. Output `(B, ..., Tq, d_v)`, weights `(B, ..., Tq, Tk)`.

    - Scores are `q k^T / sqrt(d_k)`; softmax runs over the key axis.
    - `padding_mask`: `(B, Tk)`, True (or 1) = real key. Applies to every head and query
      of that batch element. Any other shape raises `ValueError`; so do mismatched
      `q`/`k` feature sizes or `k`/`v` lengths.
    - `causal=True`: query `i` may attend key `j` iff `j <= i` (top-left aligned, like
      `torch.nn.functional.scaled_dot_product_attention(is_causal=True)`).
    - Masked weights are exactly 0; rows with at least one allowed key sum to 1.
    - All-masked rows: weights and output are all zeros (no NaN), gradients stay finite.
    """
    raise NotImplementedError("TODO: implement PT-08")
