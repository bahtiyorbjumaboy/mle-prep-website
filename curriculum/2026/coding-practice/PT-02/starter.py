from typing import Any, Callable, Iterable

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

# Canonical prompt: write a complete Dataset/DataLoader, training loop, validation loop,
# loss, optimizer, epoch metrics, and best-checkpoint tracking. Explain what breaks if
# each lifecycle call is omitted (write that explanation as comments next to each call).
#
# Mastery test: two evaluation passes on identical data are identical even when the
# model contains stochastic training-only layers (dropout) or batchnorm.

LossFn = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]


class TensorPairDataset(Dataset):
    """Row-aligned `(features[i], targets[i])` pairs.

    Raises `ValueError` if `features` and `targets` have different numbers of rows.
    """

    def __init__(self, features: torch.Tensor, targets: torch.Tensor) -> None:
        raise NotImplementedError("TODO: implement PT-02")

    def __len__(self) -> int:
        raise NotImplementedError("TODO: implement PT-02")

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        raise NotImplementedError("TODO: implement PT-02")


def make_loaders(
    train_dataset: Dataset, val_dataset: Dataset, batch_size: int, seed: int
) -> tuple[DataLoader, DataLoader]:
    """Return `(train_loader, val_loader)`.

    Training batches are shuffled reproducibly from `seed` (same seed -> same order,
    independent of the global RNG); validation batches keep dataset order. Neither
    loader drops the short final batch.
    """
    raise NotImplementedError("TODO: implement PT-02")


def train_one_epoch(
    model: nn.Module,
    loader: Iterable,
    optimizer: torch.optim.Optimizer,
    loss_fn: LossFn,
    device: torch.device | str,
) -> float:
    """One pass over `loader` with one optimizer step per batch.

    - Works whatever mode the model was left in (e.g. right after `evaluate`).
    - Gradients left on the parameters before the call must not leak into any step.
    - `loss_fn` returns the mean loss of a batch. Return the epoch loss as a Python
      float averaged over *samples* (a short final batch counts proportionally), using
      each batch's loss as computed before that batch's update.
    """
    raise NotImplementedError("TODO: implement PT-02")


def evaluate(
    model: nn.Module, loader: Iterable, loss_fn: LossFn, device: torch.device | str
) -> float | None:
    """Sample-weighted mean loss as a Python float, or `None` if the loader is empty.

    Must not change parameters or buffers, must not build autograd graphs, and must be
    deterministic for models containing dropout or batchnorm.
    """
    raise NotImplementedError("TODO: implement PT-02")


def fit(
    model: nn.Module,
    train_loader: Iterable,
    val_loader: Iterable,
    optimizer: torch.optim.Optimizer,
    loss_fn: LossFn,
    epochs: int,
    device: torch.device | str,
) -> dict[str, Any]:
    """Train for `epochs` epochs, validating after each one.

    Returns a dict with:
    - `train_loss`, `val_loss`: per-epoch lists (`val_loss` entries may be `None`);
    - `best_epoch`: 0-based epoch with the lowest validation loss (earliest on ties),
      or `None` if no epoch had a validation loss;
    - `best_val_loss`: that loss (or `None`);
    - `best_state`: a snapshot of `model.state_dict()` taken at `best_epoch` that later
      training does not modify (or `None`).
    """
    raise NotImplementedError("TODO: implement PT-02")
