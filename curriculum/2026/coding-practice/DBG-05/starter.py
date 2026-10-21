import torch
from torch import nn

# Incident: validation accuracy is noisy and well below training accuracy, GPU memory grows
# every epoch until the job dies, and the job crashes with "Expected all tensors to be on
# the same device" as soon as it runs on an accelerator.
#
# Canonical prompt: a PyTorch train/eval script has poor validation, growing GPU memory,
# and occasional device errors. Find lifecycle bugs involving `eval`, `no_grad`, graph
# retention, gradient zeroing, and device placement.
# Follow-ups: determinism test and memory trace.
#
# A `loader` is any re-iterable of `(x, y)` CPU batches with `len()`; `loss_fn` uses mean
# reduction (e.g. `nn.CrossEntropyLoss()`).


def train_step(
    model: nn.Module,
    batch: tuple[torch.Tensor, torch.Tensor],
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    device: torch.device,
) -> torch.Tensor:
    """One optimizer update on `batch` using only this batch's gradient.

    The model already lives on `device`; the batch arrives on the CPU. Returns the batch
    loss as a 0-d tensor (no `.item()` here, so the step also runs on non-CPU devices).
    """
    x, y = batch
    x = x.to(device)
    logits = model(x)
    loss = loss_fn(logits, y)
    loss.backward()
    optimizer.step()
    return loss


def train_one_epoch(
    model: nn.Module,
    loader,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    device: torch.device,
) -> float:
    """Trains for one pass over `loader` in training mode; returns the mean batch loss."""
    model.train()
    total = 0.0
    for batch in loader:
        total += train_step(model, batch, optimizer, loss_fn, device)
    return float(total / len(loader))


def evaluate(model: nn.Module, loader, loss_fn: nn.Module, device: torch.device) -> dict[str, float]:
    """Inference-mode metrics: sample-weighted mean loss and accuracy over `loader`.

    Evaluation must be deterministic, must not update any model state (e.g. BatchNorm
    running statistics), and must not build an autograd graph.
    """
    total_loss, correct, n = 0.0, 0, 0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        total_loss += loss_fn(logits, y) * len(y)
        correct += int((logits.argmax(dim=1) == y).sum().item())
        n += len(y)
    return {"loss": float(total_loss / n), "accuracy": correct / n}


def fit(
    model: nn.Module,
    train_loader,
    val_loader,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    epochs: int,
    device: torch.device,
) -> list[dict[str, float]]:
    """Alternates one training epoch and one validation pass per epoch."""
    model.to(device)
    history = []
    for _ in range(epochs):
        train_loss = train_one_epoch(model, train_loader, optimizer, loss_fn, device)
        metrics = evaluate(model, val_loader, loss_fn, device)
        history.append({"train_loss": train_loss, "val_loss": metrics["loss"], "val_accuracy": metrics["accuracy"]})
    return history
