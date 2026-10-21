import math
from typing import Any, Callable, Iterable

import torch
from torch import nn

LossFn = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]


def warmup_cosine_lambda(warmup_steps: int, total_steps: int, min_lr_ratio: float = 0.0) -> Callable[[int], float]:
    """LR multiplier for the optimizer step that follows `step` completed steps."""

    def multiplier(step: int) -> float:
        if step < warmup_steps:
            return (step + 1) / warmup_steps
        progress = min(1.0, (step - warmup_steps) / max(1, total_steps - warmup_steps))
        return min_lr_ratio + (1.0 - min_lr_ratio) * 0.5 * (1.0 + math.cos(math.pi * progress))

    return multiplier


def train_with_accumulation(
    model: nn.Module,
    microbatches: Iterable[tuple[torch.Tensor, torch.Tensor]],
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    loss_fn: LossFn,
    accumulation_steps: int,
    max_grad_norm: float,
) -> dict[str, Any]:
    if accumulation_steps < 1:
        raise ValueError("accumulation_steps must be >= 1")
    model.train()
    stats: dict[str, Any] = {"optimizer_steps": 0, "grad_norms": [], "lrs": []}

    def step(window: list[tuple[torch.Tensor, torch.Tensor]]) -> None:
        window_size = sum(len(y) for _, y in window)
        optimizer.zero_grad()
        for x, y in window:
            # loss_fn is a microbatch mean; weighting by its share of the window makes
            # the summed gradients equal the gradient of the window-wide sample mean.
            (loss_fn(model(x), y) * (len(y) / window_size)).backward()
        # One global norm over all parameters, after the window is fully accumulated.
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
        stats["grad_norms"].append(float(norm))
        stats["lrs"].append(optimizer.param_groups[0]["lr"])
        optimizer.step()
        scheduler.step()  # once per optimizer step, never per microbatch
        stats["optimizer_steps"] += 1

    window: list[tuple[torch.Tensor, torch.Tensor]] = []
    for batch in microbatches:
        window.append(batch)
        if len(window) == accumulation_steps:
            step(window)
            window = []
    if window:  # final partial window still gets an update
        step(window)
    return stats
