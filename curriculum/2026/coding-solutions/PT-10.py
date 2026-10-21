from typing import Callable

import torch
from torch import nn

LossFn = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]


def amp_config(device_type: str) -> tuple[torch.dtype | None, bool]:
    if device_type == "cuda":
        return torch.float16, True  # fp16 has a narrow exponent: scale the loss to avoid gradient underflow
    if device_type == "cpu":
        return torch.bfloat16, False  # bf16 keeps fp32's exponent range, so no scaler is needed
    return None, False  # unsupported: stay in fp32


def train_step_amp(
    model: nn.Module,
    batch: tuple[torch.Tensor, torch.Tensor],
    optimizer: torch.optim.Optimizer,
    scaler: torch.amp.GradScaler,
    loss_fn: LossFn,
    device: torch.device | str,
    amp_dtype: torch.dtype | None,
    max_grad_norm: float | None = None,
) -> float:
    device = torch.device(device)
    model.train()
    x, y = (t.to(device, non_blocking=True) for t in batch)
    optimizer.zero_grad(set_to_none=True)
    with torch.autocast(device_type=device.type, dtype=amp_dtype, enabled=amp_dtype is not None):
        loss = loss_fn(model(x), y)  # forward + loss in reduced precision where safe
    scaler.scale(loss).backward()  # backward outside autocast; grads land in fp32 master weights
    if max_grad_norm is not None:
        scaler.unscale_(optimizer)  # clip true gradients, not scaled ones
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
    scaler.step(optimizer)  # unscales if needed; skips the step on inf/NaN gradients
    scaler.update()  # back off after overflow, grow after a run of clean steps
    return loss.item()


def batched_predict(
    model: nn.Module,
    inputs: torch.Tensor,
    batch_size: int,
    device: torch.device | str,
    amp_dtype: torch.dtype | None = None,
) -> torch.Tensor:
    if batch_size < 1 or len(inputs) == 0:
        raise ValueError("need batch_size >= 1 and at least one input")
    device = torch.device(device)
    was_training = model.training
    model.eval()  # eval() changes layer behaviour (dropout off, BN running stats) ...
    outputs = []
    try:
        with torch.inference_mode():  # ... inference_mode stops autograd recording; they are independent
            for start in range(0, len(inputs), batch_size):
                chunk = inputs[start : start + batch_size].to(device, non_blocking=True)
                with torch.autocast(device_type=device.type, dtype=amp_dtype, enabled=amp_dtype is not None):
                    out = model(chunk)
                outputs.append(out.float().cpu())  # move each batch off the device: no O(dataset) device memory
    finally:
        model.train(was_training)
    return torch.cat(outputs)
