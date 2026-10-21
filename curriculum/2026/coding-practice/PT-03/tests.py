import pytest
import torch
import torch.nn.functional as F

from solution import ce_builtin, ce_log_softmax_nll, ce_manual, masked_ce_explicit, masked_ce_ignore_index

CE_FUNCS = [ce_builtin, ce_log_softmax_nll, ce_manual]
WEIGHT = torch.tensor([0.5, 2.0, 1.0, 3.0])


def _cls(n: int = 6, c: int = 4, seed: int = 0) -> tuple[torch.Tensor, torch.Tensor]:
    g = torch.Generator().manual_seed(seed)
    return torch.randn(n, c, generator=g) * 3, torch.randint(0, c, (n,), generator=g)


def _seq(b: int = 3, t: int = 5, c: int = 4, seed: int = 0) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    g = torch.Generator().manual_seed(seed)
    logits = torch.randn(b, t, c, generator=g) * 2
    targets = torch.randint(0, c, (b, t), generator=g)
    lengths = torch.tensor([t, 2, 1][:b] + [t] * max(0, b - 3))
    mask = torch.arange(t).unsqueeze(0) < lengths.unsqueeze(1)  # (B, T) right padding
    return logits, targets, mask


def _reference(logits: torch.Tensor, targets: torch.Tensor, mask: torch.Tensor, weight=None) -> torch.Tensor:
    """Explicit loop over real tokens: sum(w_y * -log p_y) / sum(w_y)."""
    num, den = torch.tensor(0.0), torch.tensor(0.0)
    for b in range(logits.shape[0]):
        for t in range(logits.shape[1]):
            if mask[b, t]:
                y = int(targets[b, t])
                w = 1.0 if weight is None else float(weight[y])
                num = num - w * torch.log_softmax(logits[b, t].double(), dim=0)[y].float()
                den = den + w
    return num / den


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("ce_builtin", "ce_log_softmax_nll", "ce_manual", "masked_ce_ignore_index", "masked_ce_explicit"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


@pytest.mark.parametrize("fn", CE_FUNCS)
@pytest.mark.parametrize("weight", [None, WEIGHT])
def test_three_ce_implementations_agree_with_reference(fn, weight):
    logits, targets = _cls()
    want = _reference(logits.unsqueeze(0), targets.unsqueeze(0), torch.ones(1, 6, dtype=torch.bool), weight)
    got = fn(logits, targets, weight=weight)
    assert got.dim() == 0 and torch.allclose(got, want, atol=1e-5)


@pytest.mark.parametrize("fn", CE_FUNCS)
def test_ce_gradients_match_builtin(fn):
    logits, targets = _cls(seed=3)
    a = logits.clone().requires_grad_()
    b = logits.clone().requires_grad_()
    fn(a, targets, weight=WEIGHT).backward()
    F.cross_entropy(b, targets, weight=WEIGHT).backward()
    assert torch.allclose(a.grad, b.grad, atol=1e-6)


@pytest.mark.parametrize("fn", CE_FUNCS)
def test_ce_is_stable_for_huge_logits(fn):
    logits = torch.tensor([[1e4, -1e4, 0.0], [-1e4, 1e4, 5e3], [3.0, 3.0, -1e4]], requires_grad=True)
    targets = torch.tensor([1, 1, 0])
    loss = fn(logits, targets)
    loss.backward()
    want = torch.tensor([2e4, 0.0, torch.log(torch.tensor(2.0)).item()]).mean()
    assert torch.isfinite(loss) and torch.allclose(loss, want, rtol=1e-6)
    assert torch.isfinite(logits.grad).all()


def test_ce_manual_does_not_call_builtin_losses(monkeypatch):
    def banned(*_args, **_kwargs):
        raise AssertionError("ce_manual must be built from logsumexp, not a built-in loss/log_softmax")

    for name in ("cross_entropy", "nll_loss", "log_softmax"):
        monkeypatch.setattr(F, name, banned)
    monkeypatch.setattr(torch, "log_softmax", banned)
    monkeypatch.setattr(torch.Tensor, "log_softmax", banned)
    logits, targets = _cls(seed=4)
    ce_manual(logits, targets, weight=WEIGHT)


@pytest.mark.parametrize("weight", [None, WEIGHT])
def test_ignore_index_loss_uses_valid_token_denominator(weight):
    logits, targets, mask = _seq()
    padded = targets.masked_fill(~mask, -100)
    got = masked_ce_ignore_index(logits, padded, weight=weight)
    assert torch.allclose(got, _reference(logits, targets, mask, weight), atol=1e-5)


def test_ignore_index_is_configurable():
    logits, targets, mask = _seq(seed=1)
    padded = targets.masked_fill(~mask, -1)
    got = masked_ce_ignore_index(logits, padded, ignore_index=-1)
    assert torch.allclose(got, _reference(logits, targets, mask), atol=1e-5)


def test_sequence_axis_not_confused_with_class_axis_when_t_equals_c():
    # T == C makes F.cross_entropy(logits_btc, targets_bt) run silently with the wrong class axis.
    logits, targets, mask = _seq(b=3, t=4, c=4, seed=2)
    padded = targets.masked_fill(~mask, -100)
    want = _reference(logits, targets, mask)
    assert torch.allclose(masked_ce_ignore_index(logits, padded), want, atol=1e-5)
    assert torch.allclose(masked_ce_explicit(logits, targets, mask), want, atol=1e-5)


@pytest.mark.parametrize("weight", [None, WEIGHT])
def test_explicit_mask_matches_reference_with_junk_padded_targets(weight):
    logits, targets, mask = _seq(seed=5)
    junk = targets.clone()
    junk[~mask] = torch.tensor([-100, 99, 7, -3, 42, 4, 1000, -1])[: int((~mask).sum())]
    got = masked_ce_explicit(logits, junk, mask, weight=weight)
    assert torch.allclose(got, _reference(logits, targets, mask, weight), atol=1e-5)


def test_explicit_mask_polarity_and_equivalence_with_ignore_index():
    logits, targets, mask = _seq(seed=6)
    a = masked_ce_explicit(logits, targets, mask, weight=WEIGHT)
    b = masked_ce_ignore_index(logits, targets.masked_fill(~mask, -100), weight=WEIGHT)
    builtin = F.cross_entropy(logits.reshape(-1, 4), targets.masked_fill(~mask, -100).reshape(-1), weight=WEIGHT)
    assert torch.allclose(a, b, atol=1e-6) and torch.allclose(a, builtin, atol=1e-6)
    flipped = masked_ce_explicit(logits, targets, ~mask, weight=WEIGHT)
    assert not torch.allclose(a, flipped)


def test_padded_positions_get_zero_gradient():
    logits, targets, mask = _seq(seed=7)
    for fn in (
        lambda z: masked_ce_explicit(z, targets, mask),
        lambda z: masked_ce_ignore_index(z, targets.masked_fill(~mask, -100)),
    ):
        z = logits.clone().requires_grad_()
        fn(z).backward()
        assert torch.isfinite(z.grad).all()
        assert torch.count_nonzero(z.grad[~mask]) == 0
        assert (z.grad[mask].abs().sum(dim=-1) > 0).all()


def test_padding_logits_do_not_leak_into_loss():
    logits, targets, mask = _seq(seed=8)
    noisy = logits.clone()
    noisy[~mask] = 1e3
    assert torch.allclose(masked_ce_explicit(noisy, targets, mask), masked_ce_explicit(logits, targets, mask))


def test_all_padding_returns_zero_with_zero_grad():
    logits = torch.randn(2, 3, 4, requires_grad=True)
    targets = torch.full((2, 3), -100)
    mask = torch.zeros(2, 3, dtype=torch.bool)
    for loss in (
        masked_ce_ignore_index(logits, targets),
        masked_ce_ignore_index(logits, targets, weight=WEIGHT),
        masked_ce_explicit(logits, targets, mask),
        masked_ce_explicit(logits, targets, mask, weight=WEIGHT),
    ):
        assert loss.dim() == 0 and torch.isfinite(loss) and loss.item() == 0.0
        loss.backward()
        assert torch.count_nonzero(logits.grad) == 0
