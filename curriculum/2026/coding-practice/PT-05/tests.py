import copy
import math

import pytest
import torch
import torch.nn.functional as F
from torch import nn

from solution import train_with_accumulation, warmup_cosine_lambda

SIZES = [3, 1, 2, 2, 1]  # with accumulation_steps=2: windows [3, 1], [2, 2], [1]


class Spy(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.modes: list[bool] = []

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        self.modes.append(self.training)
        return x


def _microbatches(sizes: list[int] = SIZES, seed: int = 0) -> list[tuple[torch.Tensor, torch.Tensor]]:
    g = torch.Generator().manual_seed(seed)
    out = []
    for n in sizes:
        x = torch.randn(n, 3, generator=g)
        out.append((x, x @ torch.tensor([[2.0, -1.0], [0.0, 1.0], [1.0, 3.0]]) + 1.0))
    return out


def _model(seed: int = 0) -> nn.Module:
    torch.manual_seed(seed)
    return nn.Linear(3, 2)


def _reference(model: nn.Module, batches, accumulation_steps, max_norm, lr_fn, base_lr):
    """Big-batch SGD: one step per window on the concatenated window."""
    windows = [batches[i : i + accumulation_steps] for i in range(0, len(batches), accumulation_steps)]
    norms, lrs = [], []
    for step, window in enumerate(windows):
        x = torch.cat([b[0] for b in window])
        y = torch.cat([b[1] for b in window])
        model.zero_grad()
        F.mse_loss(model(x), y).backward()
        grads = [p.grad for p in model.parameters()]
        norm = torch.sqrt(sum((g ** 2).sum() for g in grads))
        coef = min(1.0, max_norm / (float(norm) + 1e-6))
        lr = base_lr * lr_fn(step)
        with torch.no_grad():
            for p in model.parameters():
                p -= lr * coef * p.grad
        norms.append(float(norm))
        lrs.append(lr)
    return norms, lrs


def _run(accumulation_steps=2, max_norm=1e6, sizes=SIZES, warmup=2, total=4, stale=False):
    model = _model()
    ref = copy.deepcopy(model)
    if stale:
        for p in model.parameters():
            p.grad = torch.full_like(p, 50.0)
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    lr_fn = warmup_cosine_lambda(warmup, total, min_lr_ratio=0.1)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_fn)
    batches = _microbatches(sizes)
    stats = train_with_accumulation(model, batches, opt, sched, nn.MSELoss(), accumulation_steps, max_norm)
    norms, lrs = _reference(ref, batches, accumulation_steps, max_norm, lr_fn, 0.1)
    return model, ref, stats, norms, lrs, sched


def _assert_same_params(a: nn.Module, b: nn.Module) -> None:
    for p, q in zip(a.parameters(), b.parameters()):
        assert torch.allclose(p, q, atol=1e-6), (p, q)


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("warmup_cosine_lambda", "train_with_accumulation"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_warmup_cosine_values():
    f = warmup_cosine_lambda(3, 11, min_lr_ratio=0.1)
    assert [f(s) for s in range(3)] == pytest.approx([1 / 3, 2 / 3, 1.0])
    assert f(3) == pytest.approx(1.0)
    assert f(7) == pytest.approx(0.1 + 0.9 * 0.5)  # halfway through the cosine phase
    assert f(11) == pytest.approx(0.1) and f(50) == pytest.approx(0.1)
    g = warmup_cosine_lambda(0, 4)
    assert [g(s) for s in range(5)] == pytest.approx([0.5 * (1 + math.cos(math.pi * s / 4)) for s in range(5)])


def test_matches_big_batch_sgd_with_partial_final_window():
    model, ref, stats, norms, lrs, sched = _run()
    assert stats["optimizer_steps"] == 3 and sched.last_epoch == 3
    assert stats["lrs"] == pytest.approx(lrs) and stats["grad_norms"] == pytest.approx(norms, rel=1e-5)
    _assert_same_params(model, ref)


def test_global_norm_clipping_once_per_step():
    model, ref, stats, norms, _, _ = _run(max_norm=0.5)
    assert all(n > 0.5 for n in norms), "test setup: clipping must be active"
    assert stats["grad_norms"] == pytest.approx(norms, rel=1e-5)
    _assert_same_params(model, ref)


def test_stale_gradients_do_not_leak():
    model, ref, *_ = _run(stale=True)
    _assert_same_params(model, ref)


@pytest.mark.parametrize("accumulation_steps,steps", [(1, 5), (3, 2), (5, 1), (8, 1)])
def test_step_counts_and_trajectory_for_other_window_sizes(accumulation_steps, steps):
    model, ref, stats, norms, lrs, sched = _run(accumulation_steps=accumulation_steps, warmup=1, total=5)
    assert stats["optimizer_steps"] == steps == len(stats["lrs"]) == len(stats["grad_norms"])
    assert sched.last_epoch == steps and stats["lrs"] == pytest.approx(lrs)
    _assert_same_params(model, ref)


def test_equal_microbatches_scale_by_window():
    # Four equal microbatches, two windows: forgetting to scale doubles each update.
    model, ref, stats, *_ = _run(sizes=[2, 2, 2, 2], accumulation_steps=2)
    assert stats["optimizer_steps"] == 2
    _assert_same_params(model, ref)


def test_enables_train_mode():
    spy = Spy()
    model = nn.Sequential(spy, nn.Linear(3, 2)).eval()
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: 1.0)
    train_with_accumulation(model, _microbatches(), opt, sched, nn.MSELoss(), 2, 1.0)
    assert spy.modes and all(spy.modes)


def test_rejects_non_positive_accumulation():
    model = _model()
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: 1.0)
    with pytest.raises(ValueError):
        train_with_accumulation(model, _microbatches(), opt, sched, nn.MSELoss(), 0, 1.0)
