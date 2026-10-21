import pytest
import torch

from solution import (
    batched_scores,
    bilinear_scores,
    causal_mask,
    causal_softmax,
    embedding_lookup,
    masked_mean_pool,
    pairwise_sq_dists,
)


def _randn(*shape: int, seed: int = 0) -> torch.Tensor:
    return torch.randn(*shape, generator=torch.Generator().manual_seed(seed), dtype=torch.float64)


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in (
        "batched_scores", "bilinear_scores", "embedding_lookup", "masked_mean_pool",
        "causal_mask", "causal_softmax", "pairwise_sq_dists",
    ):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


@pytest.mark.parametrize("b,tq,tk,d", [(2, 3, 5, 4), (3, 3, 3, 3), (1, 1, 4, 2), (4, 2, 4, 2)])
def test_batched_scores_against_loop(b, tq, tk, d):
    q, k = _randn(b, tq, d, seed=1), _randn(b, tk, d, seed=2)
    want = torch.stack([q[i] @ k[i].T for i in range(b)])
    got = batched_scores(q, k)
    assert got.shape == (b, tq, tk) and torch.allclose(got, want)


@pytest.mark.parametrize("b,n,m,d,e", [(2, 3, 4, 5, 6), (3, 3, 3, 3, 3), (1, 2, 1, 4, 2)])
def test_bilinear_scores_against_loop(b, n, m, d, e):
    x, w, y = _randn(b, n, d, seed=3), _randn(d, e, seed=4), _randn(b, m, e, seed=5)
    want = torch.empty(b, n, m, dtype=torch.float64)
    for bi in range(b):
        for i in range(n):
            for j in range(m):
                want[bi, i, j] = x[bi, i] @ w @ y[bi, j]
    got = bilinear_scores(x, w, y)
    assert got.shape == (b, n, m) and torch.allclose(got, want)


def test_embedding_lookup_shapes_values_and_grad():
    table = _randn(7, 3, seed=6).requires_grad_()
    ids = torch.tensor([[0, 2, 2, 5], [5, 5, 1, 0]])  # max id < V - 1 on purpose
    out = embedding_lookup(table, ids)
    assert out.shape == (2, 4, 3)
    assert torch.equal(out[1, 2], table[1].detach()) and torch.equal(out[0, 3], table[5].detach())
    out.sum().backward()
    counts = torch.bincount(ids.flatten(), minlength=7).to(torch.float64)
    assert torch.equal(table.grad, counts.unsqueeze(1).expand(7, 3))
    assert embedding_lookup(table, torch.tensor(4)).shape == (3,)
    assert embedding_lookup(table, torch.zeros(2, 0, dtype=torch.long)).shape == (2, 0, 3)


def test_embedding_lookup_does_not_use_builtin(monkeypatch):
    import torch.nn.functional as F
    monkeypatch.setattr(F, "embedding", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no F.embedding")))
    embedding_lookup(_randn(4, 2), torch.tensor([1, 3]))


@pytest.mark.parametrize("bad", [-1, 7])
def test_embedding_lookup_rejects_out_of_range(bad):
    with pytest.raises(ValueError):
        embedding_lookup(_randn(7, 3), torch.tensor([[0, bad]]))


@pytest.mark.parametrize("b,t,d", [(2, 5, 3), (3, 4, 6), (4, 4, 4), (1, 3, 2)])
def test_masked_mean_pool_against_loop(b, t, d):
    x = _randn(b, t, d, seed=7)
    lengths = torch.tensor([t, 1, 0, 2][:b])
    mask = torch.arange(t).unsqueeze(0) < lengths.unsqueeze(1)
    if b > 2:
        mask[2] = torch.tensor([i % 2 == 1 for i in range(t)])  # non-prefix mask
    x = x.masked_fill(~mask.unsqueeze(-1), 1e9)  # garbage in padding
    got = masked_mean_pool(x, mask)
    assert got.shape == (b, d)
    for i in range(b):
        want = x[i][mask[i]].mean(dim=0) if mask[i].any() else torch.zeros(d, dtype=x.dtype)
        assert torch.allclose(got[i], want), i


def test_masked_mean_pool_all_padding_and_gradient():
    x = _randn(2, 3, 4, seed=8).requires_grad_()
    mask = torch.tensor([[True, True, False], [False, False, False]])
    out = masked_mean_pool(x, mask)
    assert torch.equal(out[1], torch.zeros(4, dtype=x.dtype)) and torch.isfinite(out).all()
    out.sum().backward()
    assert torch.allclose(x.grad[0, :2], torch.full((2, 4), 0.5, dtype=x.dtype))
    assert torch.count_nonzero(x.grad[0, 2]) == 0 and torch.count_nonzero(x.grad[1]) == 0


def test_causal_mask_polarity_and_dtype():
    m = causal_mask(4)
    assert m.dtype == torch.bool and m.shape == (4, 4)
    assert m.tolist() == [[i >= j for j in range(4)] for i in range(4)]
    assert causal_mask(1).tolist() == [[True]]
    assert causal_mask(3, device="meta").device.type == "meta"


def test_causal_softmax_masks_before_softmax():
    scores = _randn(2, 3, 5, 5, seed=9)
    w = causal_softmax(scores)
    assert w.shape == scores.shape
    future = ~torch.ones(5, 5, dtype=torch.bool).tril()
    assert torch.count_nonzero(w[..., future]) == 0
    assert torch.allclose(w.sum(dim=-1), torch.ones(2, 3, 5, dtype=w.dtype))
    for i in range(5):
        want = torch.softmax(scores[..., i, : i + 1], dim=-1)
        assert torch.allclose(w[..., i, : i + 1], want)
    assert torch.allclose(w[..., 0, 0], torch.ones(2, 3, dtype=w.dtype))


def test_causal_softmax_ignores_huge_future_scores():
    scores = torch.zeros(1, 3, 3)
    scores[0, 0, 2] = 1e4
    w = causal_softmax(scores)
    assert torch.isfinite(w).all() and torch.allclose(w[0, 1], torch.tensor([0.5, 0.5, 0.0]))
    # Legitimate scores far below a "large negative" fill value such as -1e4.
    w = causal_softmax(torch.full((1, 3, 3), -1e5))
    assert torch.allclose(w[0, 1], torch.tensor([0.5, 0.5, 0.0]))
    assert torch.allclose(w[0, 2], torch.full((3,), 1 / 3))


@pytest.mark.parametrize("b,k,d", [(3, 3, 2), (4, 2, 3), (2, 5, 4), (1, 4, 3), (4, 1, 3), (1, 1, 2)])
def test_pairwise_sq_dists_all_shapes_including_b_equals_k(b, k, d):
    a, c = _randn(b, d, seed=10), _randn(k, d, seed=11)
    want = torch.tensor([[float(((a[i] - c[j]) ** 2).sum()) for j in range(k)] for i in range(b)], dtype=a.dtype)
    got = pairwise_sq_dists(a, c)
    assert got.shape == (b, k) and torch.allclose(got, want)


def test_pairwise_sq_dists_is_nonnegative_on_identical_points():
    # float32 rows of magnitude ~30: the expanded ||a||^2 + ||b||^2 - 2ab form can round
    # below zero here unless it is clamped.
    a = torch.randn(64, 16, generator=torch.Generator().manual_seed(12)) * 3 + 30
    got = pairwise_sq_dists(a, a.clone())
    assert (got >= 0).all()
    assert torch.allclose(torch.diagonal(got), torch.zeros(64), atol=1e-1)
    assert (got + torch.eye(64) > 0).all()
