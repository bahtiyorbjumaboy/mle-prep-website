import random

import numpy as np
import pytest
import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from solution import load_checkpoint, save_checkpoint, seed_everything

EPOCHS, SPLIT = 4, 2


def _data() -> TensorDataset:
    g = torch.Generator().manual_seed(1234)
    x = torch.randn(20, 4, generator=g)
    return TensorDataset(x, x.sum(dim=1, keepdim=True))


def _build(explicit_generator: bool, generator_seed: int):
    model = nn.Sequential(nn.Linear(4, 16), nn.ReLU(), nn.Dropout(0.3), nn.Linear(16, 1))
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)  # stateful: moments + step count
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda e: 1.0 / (1 + e))  # closed-form in last_epoch
    generator = torch.Generator().manual_seed(generator_seed) if explicit_generator else None
    loader = DataLoader(_data(), batch_size=6, shuffle=True, generator=generator, num_workers=0)
    return model, optimizer, scheduler, loader, generator


def _train_epoch(model, optimizer, scheduler, loader, step: int) -> tuple[list[float], int]:
    model.train()
    losses = []
    for x, y in loader:  # shuffle order: torch RNG or the loader's generator
        jitter = random.gauss(0.0, 0.05) + float(np.random.normal(0.0, 0.05))  # Python + NumPy RNG
        optimizer.zero_grad()
        loss = F.mse_loss(model(x + jitter), y)  # dropout: torch RNG
        loss.backward()
        optimizer.step()
        losses.append(loss.item())
        step += 1
    scheduler.step()
    return losses, step


def _scramble_global_rngs() -> None:
    seed_everything(999)
    random.random(), np.random.rand(3), torch.rand(5)


@pytest.mark.parametrize("explicit_generator", [False, True])
def test_resumed_training_matches_uninterrupted_run(tmp_path, explicit_generator):
    seed_everything(0)
    model, opt, sched, loader, _ = _build(explicit_generator, generator_seed=7)
    full_losses, step = [], 0
    for _ in range(EPOCHS):
        losses, step = _train_epoch(model, opt, sched, loader, step)
        full_losses += losses
    full_state = {k: v.clone() for k, v in model.state_dict().items()}

    seed_everything(0)
    model, opt, sched, loader, gen = _build(explicit_generator, generator_seed=7)
    first_losses, step = [], 0
    for _ in range(SPLIT):
        losses, step = _train_epoch(model, opt, sched, loader, step)
        first_losses += losses
    path = tmp_path / "ckpt.pt"
    save_checkpoint(path, model, opt, sched, epoch=SPLIT, step=step, generator=gen)
    saved_step = step
    del model, opt, sched, loader, gen

    # "New process": different init, different RNG positions, new generator object.
    _scramble_global_rngs()
    model, opt, sched, loader, gen = _build(explicit_generator, generator_seed=12345)
    meta = load_checkpoint(path, model, opt, sched, generator=gen)
    assert meta == {"epoch": SPLIT, "step": saved_step}
    resumed_losses, step = [], meta["step"]
    for _ in range(meta["epoch"], EPOCHS):
        losses, step = _train_epoch(model, opt, sched, loader, step)
        resumed_losses += losses

    assert first_losses + resumed_losses == full_losses
    assert sched.last_epoch == EPOCHS and opt.param_groups[0]["lr"] == pytest.approx(0.01 / (1 + EPOCHS))
    for name, value in model.state_dict().items():
        assert torch.equal(value, full_state[name]), name


def test_load_restores_model_optimizer_scheduler_exactly(tmp_path):
    seed_everything(3)
    model, opt, sched, loader, _ = _build(False, 0)
    step = 0
    for _ in range(2):
        _, step = _train_epoch(model, opt, sched, loader, step)
    save_checkpoint(tmp_path / "c.pt", model, opt, sched, epoch=2, step=step)
    seed_everything(4)
    model2, opt2, sched2, _, _ = _build(False, 0)
    load_checkpoint(tmp_path / "c.pt", model2, opt2, sched2)
    for (k, a), b in zip(model.state_dict().items(), model2.state_dict().values()):
        assert torch.equal(a, b), k
    s1, s2 = opt.state_dict(), opt2.state_dict()
    for pid, state in s1["state"].items():
        assert torch.equal(state["exp_avg"], s2["state"][pid]["exp_avg"])
        assert torch.equal(state["exp_avg_sq"], s2["state"][pid]["exp_avg_sq"])
        assert float(state["step"]) == float(s2["state"][pid]["step"])
    assert sched2.last_epoch == sched.last_epoch == 2
    assert opt2.param_groups[0]["lr"] == opt.param_groups[0]["lr"]


def test_load_restores_global_rng_streams(tmp_path):
    seed_everything(5)
    model, opt, sched, _, gen = _build(True, 21)
    torch.rand(3), random.random(), np.random.rand(), torch.rand(2, generator=gen)
    save_checkpoint(tmp_path / "c.pt", model, opt, sched, epoch=0, step=0, generator=gen)
    expected = (torch.rand(4), random.random(), np.random.rand(2), torch.rand(3, generator=gen))
    _scramble_global_rngs()
    gen2 = torch.Generator().manual_seed(0)
    load_checkpoint(tmp_path / "c.pt", model, opt, sched, generator=gen2)
    got = (torch.rand(4), random.random(), np.random.rand(2), torch.rand(3, generator=gen2))
    assert torch.equal(got[0], expected[0]) and got[1] == expected[1]
    assert np.array_equal(got[2], expected[2]) and torch.equal(got[3], expected[3])


def test_checkpoint_is_a_real_file_loadable_safely(tmp_path):
    seed_everything(6)
    model, opt, sched, _, _ = _build(False, 0)
    path = tmp_path / "nested.pt"
    save_checkpoint(str(path), model, opt, sched, epoch=1, step=4)
    assert path.is_file() and path.stat().st_size > 0
    assert load_checkpoint(str(path), model, opt, sched) == {"epoch": 1, "step": 4}


def test_seed_everything_seeds_all_generators():
    def draw():
        return random.random(), float(np.random.rand()), torch.rand(3)

    seed_everything(11)
    a = draw()
    seed_everything(11)
    b = draw()
    seed_everything(12)
    c = draw()
    assert a[0] == b[0] and a[1] == b[1] and torch.equal(a[2], b[2])
    assert a[0] != c[0] and a[1] != c[1] and not torch.equal(a[2], c[2])


def test_seed_everything_deterministic_flag():
    previous = torch.are_deterministic_algorithms_enabled()
    cudnn = torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark
    torch.backends.cudnn.benchmark = True
    try:
        seed_everything(0, deterministic=True)
        assert torch.are_deterministic_algorithms_enabled()
        assert torch.backends.cudnn.deterministic and not torch.backends.cudnn.benchmark
    finally:
        torch.use_deterministic_algorithms(previous)
        torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = cudnn
