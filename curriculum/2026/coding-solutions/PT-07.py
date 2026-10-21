import os
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn


def seed_everything(seed: int, deterministic: bool = False) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)  # also seeds every CUDA device
    if deterministic:
        # Error on ops without a deterministic implementation instead of silently varying.
        torch.use_deterministic_algorithms(True)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def capture_rng_state(generator: torch.Generator | None = None) -> dict[str, Any]:
    np_name, np_keys, np_pos, np_has_gauss, np_gauss = np.random.get_state()
    state: dict[str, Any] = {
        "python": random.getstate(),
        # Plain Python types keep the checkpoint loadable with torch.load(weights_only=True).
        "numpy": (np_name, np_keys.tolist(), np_pos, np_has_gauss, np_gauss),
        "torch": torch.get_rng_state(),
        "cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [],
    }
    if generator is not None:  # e.g. a DataLoader's shuffling generator
        state["generator"] = generator.get_state()
    return state


def restore_rng_state(state: dict[str, Any], generator: torch.Generator | None = None) -> None:
    version, internal, gauss = state["python"]
    random.setstate((version, tuple(internal), gauss))
    np_name, np_keys, np_pos, np_has_gauss, np_gauss = state["numpy"]
    np.random.set_state((np_name, np.array(np_keys, dtype=np.uint32), np_pos, np_has_gauss, np_gauss))
    torch.set_rng_state(state["torch"])
    if state["cuda"] and torch.cuda.is_available():
        torch.cuda.set_rng_state_all(state["cuda"])
    if generator is not None:
        generator.set_state(state["generator"])


def save_checkpoint(
    path: str | Path,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    epoch: int,
    step: int,
    generator: torch.Generator | None = None,
) -> None:
    checkpoint = {
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),  # Adam moments / momentum buffers, current lr
        "scheduler": scheduler.state_dict(),  # last_epoch drives the schedule
        "epoch": epoch,
        "step": step,
        "rng": capture_rng_state(generator),
    }
    tmp = Path(f"{path}.tmp")
    torch.save(checkpoint, tmp)
    os.replace(tmp, path)  # atomic: a crash mid-write never leaves a truncated checkpoint


def load_checkpoint(
    path: str | Path,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    generator: torch.Generator | None = None,
) -> dict[str, int]:
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    model.load_state_dict(checkpoint["model"])
    optimizer.load_state_dict(checkpoint["optimizer"])
    scheduler.load_state_dict(checkpoint["scheduler"])
    restore_rng_state(checkpoint["rng"], generator)  # last, so nothing above consumes randomness
    return {"epoch": checkpoint["epoch"], "step": checkpoint["step"]}
