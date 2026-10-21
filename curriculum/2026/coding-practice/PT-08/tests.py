import math

import pytest
import torch
import torch.nn.functional as F

from solution import scaled_dot_product_attention as sdpa


def _qkv(b=2, h=3, tq=4, tk=5, dk=6, dv=7, seed=0, heads=True):
    g = torch.Generator().manual_seed(seed)
    lead = (b, h) if heads else (b,)
    return (
        torch.randn(*lead, tq, dk, generator=g, dtype=torch.float64),
        torch.randn(*lead, tk, dk, generator=g, dtype=torch.float64),
        torch.randn(*lead, tk, dv, generator=g, dtype=torch.float64),
    )


def _allowed(b, tq, tk, padding_mask=None, causal=False):
    allowed = torch.ones(b, tq, tk, dtype=torch.bool)
    if padding_mask is not None:
        allowed &= padding_mask.bool()[:, None, :]
    if causal:
        allowed &= torch.ones(tq, tk, dtype=torch.bool).tril()
    return allowed


def _loop_reference(q, k, v, allowed):
    """Per (batch, head, query) loop; `allowed` is (B, Tq, Tk)."""
    out = torch.zeros(*q.shape[:-1], v.shape[-1], dtype=q.dtype)
    w = torch.zeros(*q.shape[:-1], k.shape[-2], dtype=q.dtype)
    for b in range(q.shape[0]):
        for h in range(q.shape[1]):
            for i in range(q.shape[2]):
                keys = allowed[b, i].nonzero().flatten()
                if len(keys) == 0:
                    continue
                s = torch.stack([q[b, h, i] @ k[b, h, j] for j in keys]) / math.sqrt(q.shape[-1])
                p = torch.softmax(s, dim=0)
                w[b, h, i, keys] = p
                out[b, h, i] = (p[:, None] * v[b, h, keys]).sum(dim=0)
    return out, w


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "scaled_dot_product_attention"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_single_query():
    q = torch.tensor([[[1.0, 0.0]]])
    k = torch.tensor([[[1.0, 0.0], [0.0, 1.0]]])
    v = torch.tensor([[[1.0, 2.0], [3.0, 4.0]]])
    out, w = sdpa(q, k, v)
    p = 1 / (1 + math.exp(-1 / math.sqrt(2)))  # softmax([1/sqrt(2), 0])[0]
    assert torch.allclose(w, torch.tensor([[[p, 1 - p]]]))
    assert torch.allclose(out, torch.tensor([[[p * 1 + (1 - p) * 3, p * 2 + (1 - p) * 4]]]))


@pytest.mark.parametrize("causal", [False, True])
def test_multihead_shapes_and_loop_reference_unequal_dims(causal):
    q, k, v = _qkv(b=2, h=3, tq=4, tk=5, dk=6, dv=7)
    out, w = sdpa(q, k, v, causal=causal)
    assert out.shape == (2, 3, 4, 7) and w.shape == (2, 3, 4, 5)
    want_out, want_w = _loop_reference(q, k, v, _allowed(2, 4, 5, causal=causal))
    assert torch.allclose(w, want_w) and torch.allclose(out, want_out)


def test_padding_mask_broadcasts_over_heads_when_batch_equals_heads():
    q, k, v = _qkv(b=2, h=2, tq=3, tk=5, dk=4, dv=4, seed=1)
    pad = torch.tensor([[1, 1, 1, 0, 0], [1, 1, 1, 1, 1]], dtype=torch.bool)
    out, w = sdpa(q, k, v, padding_mask=pad)
    assert torch.count_nonzero(w[0, :, :, 3:]) == 0  # padded keys of batch 0, every head
    assert (w[1, :, :, 3:] > 0).all()  # batch 1 has no padding, every head
    want_out, want_w = _loop_reference(q, k, v, _allowed(2, 3, 5, pad))
    assert torch.allclose(w, want_w) and torch.allclose(out, want_out)


def test_padding_mask_with_more_batches_than_heads_and_int_mask():
    q, k, v = _qkv(b=3, h=2, tq=4, tk=4, dk=3, dv=5, seed=2)
    pad = torch.tensor([[1, 1, 0, 0], [1, 0, 0, 0], [1, 1, 1, 1]])
    out, w = sdpa(q, k, v, padding_mask=pad)
    want_out, want_w = _loop_reference(q, k, v, _allowed(3, 4, 4, pad))
    assert torch.allclose(w, want_w) and torch.allclose(out, want_out)


def test_combined_causal_and_padding_mastery_properties():
    q, k, v = _qkv(b=2, h=2, tq=5, tk=5, dk=4, dv=3, seed=3)
    pad = torch.tensor([[1, 1, 1, 1, 0], [1, 1, 1, 1, 1]], dtype=torch.bool)
    out, w = sdpa(q, k, v, padding_mask=pad, causal=True)
    future = ~torch.ones(5, 5, dtype=torch.bool).tril()
    assert torch.count_nonzero(w[..., future]) == 0  # causal future weights are zero
    assert torch.count_nonzero(w[0, ..., 4]) == 0  # padding weights are zero
    assert torch.allclose(w.sum(dim=-1), torch.ones(2, 2, 5, dtype=w.dtype))  # rows sum to one
    want_out, want_w = _loop_reference(q, k, v, _allowed(2, 5, 5, pad, causal=True))
    assert torch.allclose(w, want_w) and torch.allclose(out, want_out)


def test_matches_torch_sdpa_for_rectangular_causal():
    q, k, v = _qkv(b=2, h=4, tq=3, tk=6, dk=8, dv=8, seed=4)
    pad = torch.tensor([[1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1]], dtype=torch.bool)
    out, _ = sdpa(q, k, v, padding_mask=pad, causal=True)
    attn_mask = pad[:, None, None, :] & torch.ones(3, 6, dtype=torch.bool).tril()
    assert torch.allclose(out, F.scaled_dot_product_attention(q, k, v, attn_mask=attn_mask))


def test_three_dim_inputs_without_heads():
    q, k, v = _qkv(b=2, tq=3, tk=4, dk=5, dv=2, seed=5, heads=False)
    pad = torch.tensor([[1, 1, 0, 0], [1, 1, 1, 0]], dtype=torch.bool)
    out, w = sdpa(q, k, v, padding_mask=pad)
    want_out, want_w = _loop_reference(q[:, None], k[:, None], v[:, None], _allowed(2, 3, 4, pad))
    assert out.shape == (2, 3, 2) and torch.allclose(w, want_w[:, 0]) and torch.allclose(out, want_out[:, 0])


def test_scaling_uses_key_dimension_and_huge_scores_are_stable():
    q = torch.full((1, 1, 2, 4), 30.0)
    k = torch.full((1, 1, 3, 4), 30.0)
    k[..., 1, :] = -30.0
    v = torch.arange(6.0).reshape(1, 1, 3, 2)
    out, w = sdpa(q, k, v, causal=False)
    assert torch.isfinite(out).all() and torch.isfinite(w).all()
    assert torch.allclose(w[0, 0, 0], torch.tensor([0.5, 0.0, 0.5]))


def test_all_masked_rows_are_zero_and_gradients_finite():
    q, k, v = _qkv(b=2, h=2, tq=3, tk=4, dk=3, dv=2, seed=6)
    q, k, v = (t.clone().requires_grad_() for t in (q, k, v))
    pad = torch.tensor([[0, 0, 0, 0], [0, 1, 1, 1]], dtype=torch.bool)  # batch 0 fully padded
    out, w = sdpa(q, k, v, padding_mask=pad, causal=True)  # batch 1, query 0 sees only padded key 0
    assert torch.isfinite(out).all() and torch.isfinite(w).all()
    assert torch.count_nonzero(w[0]) == 0 and torch.count_nonzero(out[0]) == 0
    assert torch.count_nonzero(w[1, :, 0]) == 0 and torch.count_nonzero(out[1, :, 0]) == 0
    assert torch.allclose(w[1, :, 1:].sum(dim=-1), torch.ones(2, 2, dtype=w.dtype))
    (out.sum() + w.sum()).backward()
    for t in (q, k, v):
        assert torch.isfinite(t.grad).all()
    assert torch.count_nonzero(q.grad[0]) == 0


def test_gradients_match_torch_sdpa():
    q, k, v = _qkv(b=1, h=2, tq=3, tk=3, dk=4, dv=4, seed=7)
    a = [t.clone().requires_grad_() for t in (q, k, v)]
    b = [t.clone().requires_grad_() for t in (q, k, v)]
    sdpa(*a, causal=True)[0].pow(2).sum().backward()
    F.scaled_dot_product_attention(*b, is_causal=True).pow(2).sum().backward()
    for x, y in zip(a, b):
        assert torch.allclose(x.grad, y.grad)


def test_invalid_shapes_raise():
    q, k, v = _qkv(b=2, h=2, tq=3, tk=4, dk=3, dv=2)
    with pytest.raises(ValueError):
        sdpa(q, k, v, padding_mask=torch.ones(2, 3, dtype=torch.bool))
    with pytest.raises(ValueError):
        sdpa(q, k, v, padding_mask=torch.ones(2, 2, 4, dtype=torch.bool))
    with pytest.raises(ValueError):
        sdpa(q, k[..., :2], v)
    with pytest.raises(ValueError):
        sdpa(q, k, v[..., :3, :])
