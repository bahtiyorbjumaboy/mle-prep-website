import pytest
import torch
import torch.nn.functional as F
from torch import nn

from solution import ShapeAwareMLP

# Deliberately unequal sizes so a wrong concat/flatten axis cannot pass by coincidence.
N_CAT, EMB, N_CONT, H1, H2, C = 7, 5, 3, 11, 6, 4


def _model(dropout: float = 0.1, seed: int = 0) -> ShapeAwareMLP:
    torch.manual_seed(seed)
    return ShapeAwareMLP(
        num_categories=N_CAT,
        embedding_dim=EMB,
        num_continuous=N_CONT,
        hidden_dims=(H1, H2),
        num_classes=C,
        dropout=dropout,
    )


def _batch(b: int, seed: int = 1) -> tuple[torch.Tensor, torch.Tensor]:
    g = torch.Generator().manual_seed(seed)
    return torch.randint(0, N_CAT, (b,), generator=g), torch.randn(b, N_CONT, generator=g)


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "ShapeAwareMLP"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_is_module_with_registered_parameters():
    model = _model()
    assert isinstance(model, nn.Module)
    expected = N_CAT * EMB + (EMB + N_CONT) * H1 + H1 + H1 * H2 + H2 + H2 * C + C
    assert sum(p.numel() for p in model.parameters()) == expected
    assert all(p.requires_grad for p in model.parameters())
    embeddings = [m for m in model.modules() if isinstance(m, nn.Embedding)]
    assert len(embeddings) == 1 and embeddings[0].weight.shape == (N_CAT, EMB)
    linears = [m for m in model.modules() if isinstance(m, nn.Linear)]
    assert sorted((m.in_features, m.out_features) for m in linears) == sorted(
        [(EMB + N_CONT, H1), (H1, H2), (H2, C)]
    )
    assert sum(isinstance(m, nn.Dropout) for m in model.modules()) == 2
    assert sum(isinstance(m, nn.ReLU) for m in model.modules()) == 2


@pytest.mark.parametrize("b", [1, 2, 9])
def test_logits_shape_including_batch_of_one(b):
    model = _model().eval()
    ids, cont = _batch(b)
    out = model(ids, cont)
    assert out.shape == (b, C) and out.dtype == torch.float32


def test_returns_raw_logits_from_final_linear():
    model = _model().eval()
    final = next(m for m in model.modules() if isinstance(m, nn.Linear) and m.out_features == C)
    seen = {}
    final.register_forward_hook(lambda _m, _i, out: seen.update(out=out))
    ids, cont = _batch(6)
    out = model(ids, cont)
    assert torch.equal(out, seen["out"]), "nothing (softmax, log-softmax, ...) may follow the last Linear"
    assert not torch.allclose(torch.logsumexp(out, dim=1), torch.zeros(6))
    assert not torch.allclose(out.sum(dim=1), torch.ones(6))


def test_rows_are_independent_and_embedding_is_used():
    model = _model().eval()
    ids, cont = _batch(5)
    base = model(ids, cont)
    cont2 = cont.clone()
    cont2[2] += 3.0
    out = model(ids, cont2)
    assert torch.equal(out[[0, 1, 3, 4]], base[[0, 1, 3, 4]]) and not torch.allclose(out[2], base[2])
    ids2 = ids.clone()
    ids2[4] = (ids[4] + 1) % N_CAT
    out = model(ids2, cont)
    assert torch.equal(out[:4], base[:4]) and not torch.allclose(out[4], base[4])


def test_dropout_active_only_in_train_mode():
    model = _model(dropout=0.5)
    ids, cont = _batch(64)
    model.eval()
    assert torch.equal(model(ids, cont), model(ids, cont))
    model.train()
    torch.manual_seed(0)
    a = model(ids, cont)
    b = model(ids, cont)
    assert not torch.allclose(a, b)
    no_drop = _model(dropout=0.0).train()
    assert torch.equal(no_drop(ids, cont), no_drop.eval()(ids, cont))


def test_gradients_reach_all_parameters_and_only_used_embedding_rows():
    model = _model().train()
    ids = torch.tensor([0, 2, 2, 5])
    cont = torch.randn(4, N_CONT)
    loss = F.cross_entropy(model(ids, cont), torch.tensor([0, 1, 2, 3]))
    loss.backward()
    for name, p in model.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all(), name
    emb = next(m for m in model.modules() if isinstance(m, nn.Embedding))
    used = emb.weight.grad.abs().sum(dim=1) > 0
    assert used.tolist() == [i in {0, 2, 5} for i in range(N_CAT)]


def test_state_dict_round_trip_reproduces_logits():
    a, b = _model(seed=0).eval(), _model(seed=123).eval()
    ids, cont = _batch(4)
    assert not torch.allclose(a(ids, cont), b(ids, cont))
    b.load_state_dict(a.state_dict())
    assert torch.equal(a(ids, cont), b(ids, cont))


@pytest.mark.parametrize("bad", [-1, N_CAT, N_CAT + 10])
def test_out_of_range_ids_raise_value_error(bad):
    model = _model().eval()
    ids, cont = _batch(3)
    ids[1] = bad
    with pytest.raises(ValueError):
        model(ids, cont)


def test_hidden_dims_are_configurable():
    torch.manual_seed(0)
    model = ShapeAwareMLP(3, 2, 4, (8, 16), 9, dropout=0.0).eval()
    out = model(torch.tensor([0, 1, 2]), torch.randn(3, 4))
    assert out.shape == (3, 9)
    assert sum(p.numel() for p in model.parameters()) == 3 * 2 + 6 * 8 + 8 + 8 * 16 + 16 + 16 * 9 + 9
