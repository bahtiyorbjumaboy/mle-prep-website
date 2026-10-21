import torch
import torch.nn.functional as F

# Canonical prompt: compute CE using `F.cross_entropy`, `log_softmax+nll_loss`, and a
# manual logsumexp implementation; then compute masked sequence loss using both
# ignore-index and explicit masks.
#
# Shared contract:
# - Classification inputs: `logits` float `(N, C)` (raw scores), `targets` int64 `(N,)`.
# - Sequence inputs: `logits` `(B, T, C)`, `targets` `(B, T)`.
# - Optional `weight` is a `(C,)` class-weight tensor. Weighted means follow PyTorch:
#   `sum_i weight[y_i] * loss_i / sum_i weight[y_i]` over the counted tokens only.
# - Every function returns a 0-dim tensor connected to `logits` (so `.backward()` works)
#   and stays finite for logits as large as +/-1e4.
# - Masked losses average over real tokens only. If no token counts (all padding, or all
#   counted weights are zero) they return 0 instead of NaN, with zero gradients.


def ce_builtin(logits: torch.Tensor, targets: torch.Tensor, weight: torch.Tensor | None = None) -> torch.Tensor:
    """Mean CE via `F.cross_entropy`."""
    raise NotImplementedError("TODO: implement PT-03")


def ce_log_softmax_nll(
    logits: torch.Tensor, targets: torch.Tensor, weight: torch.Tensor | None = None
) -> torch.Tensor:
    """Mean CE via `F.log_softmax` followed by `F.nll_loss`."""
    raise NotImplementedError("TODO: implement PT-03")


def ce_manual(logits: torch.Tensor, targets: torch.Tensor, weight: torch.Tensor | None = None) -> torch.Tensor:
    """Mean CE from `torch.logsumexp` and indexing only.

    Do not call `cross_entropy`, `nll_loss`, or any `log_softmax`.
    """
    raise NotImplementedError("TODO: implement PT-03")


def masked_ce_ignore_index(
    logits: torch.Tensor,
    targets: torch.Tensor,
    ignore_index: int = -100,
    weight: torch.Tensor | None = None,
) -> torch.Tensor:
    """Token-mean sequence CE where positions with `targets == ignore_index` are padding."""
    raise NotImplementedError("TODO: implement PT-03")


def masked_ce_explicit(
    logits: torch.Tensor,
    targets: torch.Tensor,
    mask: torch.Tensor,
    weight: torch.Tensor | None = None,
) -> torch.Tensor:
    """Token-mean sequence CE where `mask` `(B, T)` is True for real tokens.

    Targets at padded positions are arbitrary (they may be negative or >= C).
    """
    raise NotImplementedError("TODO: implement PT-03")
