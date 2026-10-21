import torch
import torch.nn.functional as F


def ce_builtin(logits: torch.Tensor, targets: torch.Tensor, weight: torch.Tensor | None = None) -> torch.Tensor:
    return F.cross_entropy(logits, targets, weight=weight)


def ce_log_softmax_nll(
    logits: torch.Tensor, targets: torch.Tensor, weight: torch.Tensor | None = None
) -> torch.Tensor:
    return F.nll_loss(F.log_softmax(logits, dim=1), targets, weight=weight)


def ce_manual(logits: torch.Tensor, targets: torch.Tensor, weight: torch.Tensor | None = None) -> torch.Tensor:
    # logits (N, C), targets (N,). -log softmax(z)_y = logsumexp(z) - z_y; logsumexp
    # subtracts the row max internally, so +/-1e4 logits stay finite.
    per_example = torch.logsumexp(logits, dim=1) - logits.gather(1, targets.unsqueeze(1)).squeeze(1)  # (N,)
    if weight is None:
        return per_example.mean()
    w = weight[targets]  # (N,) weighted mean divides by the sum of the weights used
    return (w * per_example).sum() / w.sum()


def masked_ce_ignore_index(
    logits: torch.Tensor,
    targets: torch.Tensor,
    ignore_index: int = -100,
    weight: torch.Tensor | None = None,
) -> torch.Tensor:
    # logits (B, T, C) -> (B*T, C); passing (B, T, C) directly would treat T as the class axis.
    flat_logits = logits.reshape(-1, logits.shape[-1])
    flat_targets = targets.reshape(-1)  # (B*T,)
    total = F.cross_entropy(flat_logits, flat_targets, weight=weight, ignore_index=ignore_index, reduction="sum")
    valid = flat_targets != ignore_index
    denom = valid.sum() if weight is None else weight[flat_targets[valid]].sum()
    # reduction="mean" would return 0/0 = NaN for an all-padding batch; the sum is 0 there.
    return total / denom if denom > 0 else total


def masked_ce_explicit(
    logits: torch.Tensor,
    targets: torch.Tensor,
    mask: torch.Tensor,
    weight: torch.Tensor | None = None,
) -> torch.Tensor:
    mask = mask.bool()  # (B, T), True = real token
    safe_targets = targets.masked_fill(~mask, 0)  # padded targets may be junk / out of range
    per_token = F.cross_entropy(
        logits.reshape(-1, logits.shape[-1]), safe_targets.reshape(-1), weight=weight, reduction="none"
    ).reshape(mask.shape)  # (B, T), already multiplied by weight[target]
    token_weight = mask.to(per_token.dtype)
    if weight is not None:
        token_weight = token_weight * weight[safe_targets]
    total = torch.where(mask, per_token, torch.zeros_like(per_token)).sum()  # mask before reducing
    denom = token_weight.sum()
    return total / denom if denom > 0 else total
