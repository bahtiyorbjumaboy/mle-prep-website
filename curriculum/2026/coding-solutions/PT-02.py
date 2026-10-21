import copy
from typing import Any, Callable, Iterable

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

LossFn = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]


class TensorPairDataset(Dataset):
    """Row-aligned (features, targets) pairs."""

    def __init__(self, features: torch.Tensor, targets: torch.Tensor) -> None:
        if len(features) != len(targets):
            raise ValueError("features and targets must have the same number of rows")
        self.features = features
        self.targets = targets

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.features[index], self.targets[index]


def make_loaders(
    train_dataset: Dataset, val_dataset: Dataset, batch_size: int, seed: int
) -> tuple[DataLoader, DataLoader]:
    """Seeded shuffling for training; fixed order for validation; keep short final batches."""
    generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, generator=generator)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader


def train_one_epoch(
    model: nn.Module,
    loader: Iterable,
    optimizer: torch.optim.Optimizer,
    loss_fn: LossFn,
    device: torch.device | str,
) -> float:
    model.train()  # without it, dropout/batchnorm stay in inference behaviour after evaluate()
    total, count = 0.0, 0
    for features, targets in loader:
        features, targets = features.to(device), targets.to(device)
        optimizer.zero_grad()  # without it, gradients from previous steps accumulate
        loss = loss_fn(model(features), targets)
        loss.backward()  # without it, .grad is never populated and step() does nothing
        optimizer.step()  # without it, parameters never change
        n = len(targets)
        total += loss.item() * n  # .item() detaches; summing tensors would retain every graph
        count += n
    return total / count


def evaluate(
    model: nn.Module, loader: Iterable, loss_fn: LossFn, device: torch.device | str
) -> float | None:
    model.eval()  # without it, dropout is random and batchnorm updates its running stats
    total, count = 0.0, 0
    with torch.no_grad():  # without it, autograd builds (and holds memory for) unused graphs
        for features, targets in loader:
            features, targets = features.to(device), targets.to(device)
            n = len(targets)
            total += loss_fn(model(features), targets).item() * n
            count += n
    return total / count if count else None


def fit(
    model: nn.Module,
    train_loader: Iterable,
    val_loader: Iterable,
    optimizer: torch.optim.Optimizer,
    loss_fn: LossFn,
    epochs: int,
    device: torch.device | str,
) -> dict[str, Any]:
    model.to(device)
    history: dict[str, Any] = {
        "train_loss": [], "val_loss": [], "best_epoch": None, "best_val_loss": None, "best_state": None,
    }
    for epoch in range(epochs):
        history["train_loss"].append(train_one_epoch(model, train_loader, optimizer, loss_fn, device))
        val_loss = evaluate(model, val_loader, loss_fn, device)
        history["val_loss"].append(val_loss)
        if val_loss is not None and (history["best_val_loss"] is None or val_loss < history["best_val_loss"]):
            history["best_epoch"] = epoch
            history["best_val_loss"] = val_loss
            # state_dict() returns live references; without a copy the "best" silently tracks the latest.
            history["best_state"] = copy.deepcopy(model.state_dict())
    return history
