import math
from typing import Any, Callable, Iterable

import torch
from torch import nn

# Canonical prompt: modify a training loop to emulate a larger batch with microbatches,
# add global-norm clipping, and apply warmup + cosine scheduling at the correct cadence.
# Follow-ups: partial final accumulation window; why BatchNorm breaks exact equivalence.
#
# The loop you are modifying (one optimizer step per microbatch):
#
#     for x, y in loader:
#         optimizer.zero_grad()
#         loss = loss_fn(model(x), y)
#         loss.backward()
#         optimizer.step()

LossFn = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]


def warmup_cosine_lambda(warmup_steps: int, total_steps: int, min_lr_ratio: float = 0.0) -> Callable[[int], float]:
    """Return `f(step) -> float` for `torch.optim.lr_scheduler.LambdaLR`.

    `step` = number of optimizer steps already taken, so the first update uses `f(0)`.
    - `step < warmup_steps`: linear warmup `(step + 1) / warmup_steps`.
    - otherwise: `progress = min(1, (step - warmup_steps) / max(1, total_steps - warmup_steps))`
      and `f = min_lr_ratio + (1 - min_lr_ratio) * 0.5 * (1 + cos(pi * progress))`.
    """
    raise NotImplementedError("TODO: implement PT-05")


def train_with_accumulation(
    model: nn.Module,
    microbatches: Iterable[tuple[torch.Tensor, torch.Tensor]],
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    loss_fn: LossFn,
    accumulation_steps: int,
    max_grad_norm: float,
) -> dict[str, Any]:
    """One epoch with gradient accumulation.

    Contract:
    - Consecutive groups of `accumulation_steps` microbatches form a window; a shorter
      final window is still applied. `accumulation_steps < 1` raises `ValueError`.
    - `loss_fn` returns the mean loss of one microbatch; microbatches may differ in size.
      Each optimizer step must use exactly the gradient of the mean loss over all
      samples in its window (as if the window were one big batch).
    - Gradients present before the call must not leak into any step.
    - Before each step, clip the gradient's global L2 norm (over all parameters
      together) to `max_grad_norm`.
    - The scheduler advances once per optimizer step, after that step.
    - Return `{"optimizer_steps": int, "grad_norms": [pre-clip global norm per step],
      "lrs": [learning rate of param group 0 used by each step]}`.
    """
    raise NotImplementedError("TODO: implement PT-05")
