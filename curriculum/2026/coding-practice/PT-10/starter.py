from typing import Callable

import torch
from torch import nn

# Canonical prompt: starting from a correct FP32 training/inference loop, add
# device-aware autocast and gradient scaling where appropriate, then implement
# memory-bounded batched inference with `eval()` and inference/no-grad semantics.
# Collect outputs without retaining graphs.
# Follow-ups: CPU fallback; unsupported ops; overflow/underflow; why `eval()` and
# `no_grad`/`inference_mode` solve different problems.
#
# The FP32 starting point:
#
#     def train_step(model, batch, optimizer, loss_fn, device):
#         model.train()
#         x, y = (t.to(device) for t in batch)
#         optimizer.zero_grad()
#         loss = loss_fn(model(x), y)
#         loss.backward()
#         optimizer.step()
#         return loss.item()
#
#     def predict(model, inputs):
#         return model(inputs)
#
# CPU note: tests run CPU bfloat16 autocast and a real CPU `torch.amp.GradScaler`
# (scaling, unscaling, inf-step skipping). CUDA fp16 numerics and GPU memory behaviour
# are only exercised when CUDA is available.

LossFn = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]


def amp_config(device_type: str) -> tuple[torch.dtype | None, bool]:
    """Return `(autocast_dtype, use_grad_scaler)` for a device type.

    `"cuda"` -> `(torch.float16, True)`; `"cpu"` -> `(torch.bfloat16, False)`;
    anything else -> `(None, False)` (stay in FP32).
    """
    raise NotImplementedError("TODO: implement PT-10")


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
    """The FP32 `train_step` with mixed precision added.

    - Forward and loss run under `torch.autocast` for `device`'s type with `amp_dtype`
      (disabled when `amp_dtype is None`); parameters stay FP32.
    - Use `scaler` for backward and the optimizer step (it may be disabled, in which
      case it is a pass-through), and update its scale every step.
    - If `max_grad_norm` is given, clip the global norm of the *unscaled* gradients.
    - An overflowing step (inf/NaN gradients) must leave the parameters unchanged.
    - Returns the loss as a Python float.
    """
    raise NotImplementedError("TODO: implement PT-10")


def batched_predict(
    model: nn.Module,
    inputs: torch.Tensor,
    batch_size: int,
    device: torch.device | str,
    amp_dtype: torch.dtype | None = None,
) -> torch.Tensor:
    """Run `model` over `inputs` in chunks of at most `batch_size` rows.

    - Evaluation-mode layers and no autograd recording while predicting; the model's
      previous train/eval mode is restored afterwards.
    - Optional autocast with `amp_dtype`.
    - Returns one FP32 CPU tensor in input order, with no autograd history.
    - `batch_size < 1` or empty `inputs` raise `ValueError`.
    """
    raise NotImplementedError("TODO: implement PT-10")
