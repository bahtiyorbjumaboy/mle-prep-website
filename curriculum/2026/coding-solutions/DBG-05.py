import torch
from torch import nn

# Repair of the DBG-05 starter. The lifecycle bugs and their fixes:
# 1. Device placement: only `x` was moved, so the loss mixed device and CPU tensors.
#    Fix: move `y` too (checked on the `meta` device, which raises like a GPU would).
# 2. Gradient zeroing: without `zero_grad`, every step applied the sum of all previous
#    batches' gradients. Fix: clear gradients before each backward pass.
# 3. Graph retention: `total += loss` kept every step's autograd graph alive for the whole
#    epoch. Fix: return `loss.detach()`. Detaching earlier (logits or loss before
#    `backward`) would silently stop learning instead.
# 4. `eval`: dropout and BatchNorm stayed in training mode during validation (noisy,
#    pessimistic metrics, and running statistics updated from validation data). Fix:
#    `model.eval()`; `train_one_epoch` already switches back with `model.train()`.
# 5. `no_grad`: validation built a graph per batch and the tensor accumulator kept all of
#    them alive. Fix: run evaluation under `torch.no_grad()`.
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
    x, y = x.to(device), y.to(device)
    optimizer.zero_grad(set_to_none=True)
    logits = model(x)
    loss = loss_fn(logits, y)
    loss.backward()
    optimizer.step()
    return loss.detach()


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
    model.eval()
    total_loss, correct, n = 0.0, 0, 0
    with torch.no_grad():
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
