import copy

import pytest
import torch
import torch.nn.functional as F
from torch import nn

from solution import amp_config, batched_predict, train_step_amp


class Spy(nn.Module):
    """Records batch size, mode, and grad state on every forward call."""

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[int, bool, bool]] = []

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        self.calls.append((x.shape[0], self.training, torch.is_grad_enabled()))
        return x


def _model(seed: int = 0, dropout: float = 0.0) -> nn.Sequential:
    torch.manual_seed(seed)
    return nn.Sequential(nn.Linear(4, 16), nn.ReLU(), nn.Dropout(dropout), nn.Linear(16, 3))


def _batch(n: int = 8, seed: int = 1) -> tuple[torch.Tensor, torch.Tensor]:
    g = torch.Generator().manual_seed(seed)
    return torch.randn(n, 4, generator=g), torch.randn(n, 3, generator=g)


def _fp32_reference_step(model: nn.Module, batch, lr: float, max_norm: float | None = None) -> float:
    opt = torch.optim.SGD(model.parameters(), lr=lr)
    opt.zero_grad()
    loss = F.mse_loss(model(batch[0]), batch[1])
    loss.backward()
    if max_norm is not None:
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)
    opt.step()
    return loss.item()


def _assert_params_close(a: nn.Module, b: nn.Module, **tol) -> None:
    for p, q in zip(a.parameters(), b.parameters()):
        assert torch.allclose(p, q, **tol)


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("amp_config", "train_step_amp", "batched_predict"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_amp_config_is_device_aware():
    assert amp_config("cuda") == (torch.float16, True)
    assert amp_config("cpu") == (torch.bfloat16, False)
    assert amp_config("mps") == (None, False)


@pytest.mark.parametrize("scaler_enabled", [True, False])
def test_scaled_step_matches_fp32_step(scaler_enabled):
    # Autocast off isolates the scaler lifecycle; a real CPU GradScaler multiplies the loss by 65536.
    model, ref = _model(), _model()
    batch = _batch()
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    scaler = torch.amp.GradScaler("cpu", enabled=scaler_enabled)
    loss = train_step_amp(model, batch, opt, scaler, nn.MSELoss(), "cpu", amp_dtype=None)
    want = _fp32_reference_step(ref, batch, lr=0.1)
    assert type(loss) is float and loss == pytest.approx(want, rel=1e-6)
    _assert_params_close(model, ref, atol=1e-6)
    assert all(p.dtype == torch.float32 for p in model.parameters())


def test_clipping_uses_unscaled_gradients():
    model, ref = _model(), _model()
    batch = _batch(seed=2)
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    scaler = torch.amp.GradScaler("cpu")
    train_step_amp(model, batch, opt, scaler, nn.MSELoss(), torch.device("cpu"), None, max_grad_norm=0.05)
    _fp32_reference_step(ref, batch, lr=0.1, max_norm=0.05)
    _assert_params_close(model, ref, atol=1e-6)
    assert any(not torch.equal(p, q) for p, q in zip(model.parameters(), _model().parameters()))


def test_overflow_step_is_skipped_and_scale_backs_off():
    model = _model()
    before = copy.deepcopy(model.state_dict())
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    scaler = torch.amp.GradScaler("cpu", init_scale=1024.0)
    x, y = _batch()
    x[0, 0] = float("inf")
    train_step_amp(model, (x, y), opt, scaler, nn.MSELoss(), "cpu", None)
    for k, v in model.state_dict().items():
        assert torch.equal(v, before[k]), k
    assert scaler.get_scale() == 512.0
    train_step_amp(model, _batch(), opt, scaler, nn.MSELoss(), "cpu", None)  # recovers on the next clean step
    assert all(torch.isfinite(p).all() for p in model.parameters())
    assert any(not torch.equal(v, before[k]) for k, v in model.state_dict().items())


def test_cpu_bf16_autocast_runs_forward_in_reduced_precision():
    model, ref = _model(), _model()
    dtypes = []
    model[0].register_forward_hook(lambda m, i, o: dtypes.append(o.dtype))
    batch = _batch(seed=3)
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    dtype, use_scaler = amp_config("cpu")
    scaler = torch.amp.GradScaler("cpu", enabled=use_scaler)
    loss = train_step_amp(model, batch, opt, scaler, nn.MSELoss(), "cpu", dtype)
    want = _fp32_reference_step(ref, batch, lr=0.1)
    assert dtypes == [torch.bfloat16]
    assert all(p.dtype == torch.float32 for p in model.parameters())  # fp32 master weights
    assert loss == pytest.approx(want, rel=5e-2)
    _assert_params_close(model, ref, atol=5e-3)


def test_train_step_sets_train_mode():
    spy = Spy()
    model = nn.Sequential(spy, _model()).eval()
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    train_step_amp(model, _batch(), opt, torch.amp.GradScaler("cpu"), nn.MSELoss(), "cpu", None)
    assert spy.calls and all(training and grad for _, training, grad in spy.calls)


@pytest.mark.parametrize("initially_training", [True, False])
def test_batched_predict_order_chunks_modes_and_no_graph(initially_training):
    spy = Spy()
    model = nn.Sequential(spy, _model(dropout=0.5))
    model.train(initially_training)
    x = torch.randn(10, 4, generator=torch.Generator().manual_seed(4))
    out = batched_predict(model, x, batch_size=4, device="cpu")
    assert [n for n, _, _ in spy.calls] == [4, 4, 2]
    assert all(not training and not grad for _, training, grad in spy.calls)
    assert model.training is initially_training  # previous mode restored
    assert out.shape == (10, 3) and out.dtype == torch.float32 and out.device.type == "cpu"
    assert not out.requires_grad and out.grad_fn is None
    with torch.no_grad():
        want = model[1].eval()(x)
    assert torch.allclose(out, want, atol=1e-6)
    assert all(p.grad is None and p.requires_grad for p in model.parameters())


def test_batched_predict_is_deterministic_with_dropout_and_batch_size_invariant():
    model = _model(dropout=0.5).train()
    x = torch.randn(7, 4, generator=torch.Generator().manual_seed(5))
    a = batched_predict(model, x, 3, "cpu")
    b = batched_predict(model, x, 3, "cpu")
    c = batched_predict(model, x, 100, "cpu")
    d = batched_predict(model, x, 1, "cpu")
    assert torch.equal(a, b) and torch.allclose(a, c, atol=1e-6) and torch.allclose(a, d, atol=1e-6)


def test_batched_predict_bf16_matches_fp32_fixture_and_returns_fp32():
    model = _model(seed=6)
    x = torch.randn(9, 4, generator=torch.Generator().manual_seed(6))
    out = batched_predict(model, x, 4, "cpu", amp_dtype=torch.bfloat16)
    with torch.no_grad():
        want = model.eval()(x)
    assert out.dtype == torch.float32
    assert torch.allclose(out, want, rtol=3e-2, atol=3e-2) and not torch.equal(out, want)


def test_batched_predict_rejects_bad_arguments():
    model = _model()
    with pytest.raises(ValueError):
        batched_predict(model, torch.randn(3, 4), 0, "cpu")
    with pytest.raises(ValueError):
        batched_predict(model, torch.empty(0, 4), 2, "cpu")


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA-only: fp16 autocast/GradScaler and GPU memory")
def test_cuda_fp16_amp_and_bounded_device_memory():
    device = torch.device("cuda")
    model, ref = _model().to(device), _model().to(device)
    batch = tuple(t.to(device) for t in _batch())
    dtype, use_scaler = amp_config("cuda")
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    train_step_amp(model, batch, opt, torch.amp.GradScaler("cuda", enabled=use_scaler), nn.MSELoss(), device, dtype)
    _fp32_reference_step(ref, batch, lr=0.1)
    _assert_params_close(model, ref, atol=1e-2)
    torch.cuda.synchronize()
    baseline = torch.cuda.memory_allocated()
    out = batched_predict(model, torch.randn(4096, 4), 256, device, amp_dtype=dtype)
    torch.cuda.synchronize()
    assert out.device.type == "cpu" and torch.cuda.memory_allocated() <= baseline
