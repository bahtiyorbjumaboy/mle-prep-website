import copy

import pytest
import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from solution import TensorPairDataset, evaluate, fit, make_loaders, train_one_epoch


class Spy(nn.Module):
    """Records (training flag, grad enabled) on every forward call."""

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[bool, bool]] = []

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        self.calls.append((self.training, torch.is_grad_enabled()))
        return x


def _data(n: int = 7, seed: int = 0) -> tuple[torch.Tensor, torch.Tensor]:
    g = torch.Generator().manual_seed(seed)
    x = torch.randn(n, 3, generator=g)
    return x, x @ torch.tensor([[1.0, -2.0], [0.5, 0.0], [-1.0, 3.0]]) + 0.1 * torch.randn(n, 2, generator=g)


def _loader(x: torch.Tensor, y: torch.Tensor, batch_size: int = 3) -> DataLoader:
    return DataLoader(TensorDataset(x, y), batch_size=batch_size, shuffle=False)


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("TensorPairDataset", "make_loaders", "train_one_epoch", "evaluate", "fit"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_dataset_len_getitem_and_validation():
    x, y = _data(5)
    ds = TensorPairDataset(x, y)
    assert len(ds) == 5
    fx, fy = ds[3]
    assert torch.equal(fx, x[3]) and torch.equal(fy, y[3])
    with pytest.raises(ValueError):
        TensorPairDataset(x, y[:4])


def test_make_loaders_seeded_shuffle_and_short_final_batch():
    ids = torch.arange(10).float().unsqueeze(1)
    ds = TensorPairDataset(ids, ids.squeeze(1))
    train1, val = make_loaders(ds, ds, batch_size=4, seed=7)
    torch.manual_seed(999)  # global RNG must not decide the order
    order1 = torch.cat([y for _, y in train1]).tolist()
    train2, _ = make_loaders(ds, ds, batch_size=4, seed=7)
    torch.manual_seed(0)
    order2 = torch.cat([y for _, y in train2]).tolist()
    train3, _ = make_loaders(ds, ds, batch_size=4, seed=8)
    order3 = torch.cat([y for _, y in train3]).tolist()
    assert sorted(order1) == list(range(10)) and order1 == order2
    assert order1 != list(range(10)) and order1 != order3
    assert [len(y) for _, y in train1] == [4, 4, 2]
    assert torch.cat([y for _, y in val]).tolist() == list(range(10))
    assert [len(y) for _, y in val] == [4, 4, 2]


def _reference_epoch(model: nn.Module, loader: DataLoader, lr: float) -> float:
    total, count = 0.0, 0
    for x, y in loader:
        model.zero_grad()
        loss = F.mse_loss(model(x), y)
        loss.backward()
        with torch.no_grad():
            for p in model.parameters():
                p -= lr * p.grad
        total += loss.item() * len(y)
        count += len(y)
    return total / count


def test_train_one_epoch_matches_manual_sgd_with_short_batch_and_stale_grads():
    x, y = _data(7)
    torch.manual_seed(0)
    model = nn.Linear(3, 2)
    ref = copy.deepcopy(model)
    for p in model.parameters():
        p.grad = torch.full_like(p, 100.0)  # stale gradients from "somewhere else"
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    got = train_one_epoch(model, _loader(x, y), opt, nn.MSELoss(), "cpu")
    want = _reference_epoch(ref, _loader(x, y), lr=0.1)
    assert type(got) is float
    assert got == pytest.approx(want, rel=1e-6)
    for p, q in zip(model.parameters(), ref.parameters()):
        assert torch.allclose(p, q, atol=1e-6)


def test_train_loss_is_sample_weighted_not_batch_averaged():
    # Zero learning rate isolates the aggregation: batches of 3, 3, 1 samples.
    x, y = _data(7)
    model = nn.Linear(3, 2)
    opt = torch.optim.SGD(model.parameters(), lr=0.0)
    got = train_one_epoch(model, _loader(x, y), opt, nn.MSELoss(), "cpu")
    with torch.no_grad():
        exact = F.mse_loss(model(x), y, reduction="none").mean(dim=1).mean().item()
        batch_means = [F.mse_loss(model(xb), yb).item() for xb, yb in _loader(x, y)]
    assert got == pytest.approx(exact, rel=1e-6)
    assert abs(got - sum(batch_means) / len(batch_means)) > 1e-4


def test_train_one_epoch_enables_train_mode_and_grad():
    x, y = _data(7)
    spy = Spy()
    model = nn.Sequential(spy, nn.Linear(3, 2), nn.Dropout(0.5))
    model.eval()  # e.g. left over from the previous validation pass
    train_one_epoch(model, _loader(x, y), torch.optim.SGD(model.parameters(), lr=0.01), nn.MSELoss(), "cpu")
    assert spy.calls and all(training and grad for training, grad in spy.calls)


def test_evaluate_uses_eval_mode_and_no_grad():
    x, y = _data(7)
    spy = Spy()
    model = nn.Sequential(spy, nn.Linear(3, 2), nn.Dropout(0.5))
    model.train()
    evaluate(model, _loader(x, y), nn.MSELoss(), torch.device("cpu"))
    assert spy.calls and all(not training and not grad for training, grad in spy.calls)


def test_evaluate_is_exact_sample_weighted_and_returns_float():
    x, y = _data(7)
    torch.manual_seed(1)
    model = nn.Linear(3, 2)
    got = evaluate(model, _loader(x, y), nn.MSELoss(), "cpu")
    with torch.no_grad():
        exact = F.mse_loss(model(x), y).item()
    assert type(got) is float and got == pytest.approx(exact, rel=1e-6)


def test_two_evaluation_passes_identical_and_state_untouched():
    x, y = _data(9)
    torch.manual_seed(2)
    model = nn.Sequential(nn.Linear(3, 8), nn.BatchNorm1d(8), nn.ReLU(), nn.Dropout(0.5), nn.Linear(8, 2))
    model.train()
    model(torch.randn(16, 3))  # give batchnorm non-trivial running stats
    before = copy.deepcopy(model.state_dict())
    a = evaluate(model, _loader(x, y, 4), nn.MSELoss(), "cpu")
    b = evaluate(model, _loader(x, y, 4), nn.MSELoss(), "cpu")
    assert a == b
    after = model.state_dict()
    assert all(torch.equal(before[k], after[k]) for k in before), "evaluate changed params or buffers"
    with torch.no_grad():
        assert a == pytest.approx(F.mse_loss(model.eval()(x), y).item(), rel=1e-6)


def test_evaluate_empty_loader_returns_none():
    model = nn.Linear(3, 2)
    empty = DataLoader(TensorDataset(torch.empty(0, 3), torch.empty(0, 2)), batch_size=4)
    assert evaluate(model, empty, nn.MSELoss(), "cpu") is None


def _overshoot_setup(lr: float = 0.1) -> tuple[nn.Module, DataLoader, DataLoader, torch.optim.Optimizer]:
    # Train target y = 2x, validation target y = 0.5x, start at w = -1: validation loss
    # improves while w passes 0.5 and then worsens, so the best epoch is not the last one.
    model = nn.Linear(1, 1, bias=False)
    with torch.no_grad():
        model.weight.fill_(-1.0)
    ones = torch.ones(4, 1)
    train = DataLoader(TensorDataset(ones, 2 * ones), batch_size=2)
    val = DataLoader(TensorDataset(ones[:2], 0.5 * ones[:2]), batch_size=2)
    return model, train, val, torch.optim.SGD(model.parameters(), lr=lr)


def test_fit_tracks_best_checkpoint_as_independent_snapshot():
    model, train, val, opt = _overshoot_setup()
    out = fit(model, train, val, opt, nn.MSELoss(), epochs=4, device="cpu")
    assert len(out["train_loss"]) == len(out["val_loss"]) == 4
    assert all(type(v) is float for v in out["train_loss"] + out["val_loss"])
    vals = out["val_loss"]
    assert out["best_epoch"] == vals.index(min(vals)) == 1  # interior best epoch
    assert out["best_val_loss"] == pytest.approx(min(vals))
    assert out["best_state"]["weight"].item() == pytest.approx(2 - 3 * 0.8 ** 4, abs=1e-5)
    assert model.weight.item() == pytest.approx(2 - 3 * 0.8 ** 8, abs=1e-5)
    restored = nn.Linear(1, 1, bias=False)
    restored.load_state_dict(out["best_state"])
    assert evaluate(restored, val, nn.MSELoss(), "cpu") == pytest.approx(out["best_val_loss"], rel=1e-6)


def test_fit_ties_keep_earliest_epoch():
    model, train, val, opt = _overshoot_setup(lr=0.0)
    out = fit(model, train, val, opt, nn.MSELoss(), epochs=3, device="cpu")
    assert out["val_loss"][0] == out["val_loss"][2] and out["best_epoch"] == 0


def test_fit_with_empty_validation():
    model, train, _, opt = _overshoot_setup()
    empty = DataLoader(TensorDataset(torch.empty(0, 1), torch.empty(0, 1)), batch_size=2)
    out = fit(model, train, empty, opt, nn.MSELoss(), epochs=2, device="cpu")
    assert len(out["train_loss"]) == 2 and out["val_loss"] == [None, None]
    assert out["best_epoch"] is None and out["best_val_loss"] is None and out["best_state"] is None
