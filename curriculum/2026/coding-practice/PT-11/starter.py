from typing import Iterable

import torch
from torch import nn

# Canonical prompt: given a pretrained backbone and new head, freeze the backbone, train
# only the head, then unfreeze selected layers with a lower learning rate via optimizer
# parameter groups. Verify which parameters receive gradients and optimizer updates.
# Follow-ups: BatchNorm behavior while frozen; rebuilding optimizer after unfreeze;
# discriminative LR; what compute/memory freezing does and does not save.
#
# `model` has two submodules: `model.backbone` (pretrained, may contain BatchNorm) and
# `model.head` (new). Layer names are paths inside the backbone, e.g. "block2".


def freeze_backbone(model: nn.Module) -> None:
    """Make every backbone parameter non-trainable and every head parameter trainable."""
    raise NotImplementedError("TODO: implement PT-11")


def make_optimizer(model: nn.Module, head_lr: float, momentum: float = 0.9) -> torch.optim.SGD:
    """SGD (with `momentum`) owning exactly the currently trainable parameters, in one group."""
    raise NotImplementedError("TODO: implement PT-11")


def set_train_mode(model: nn.Module) -> None:
    """Put the model in training mode, except that a BatchNorm layer whose affine
    parameters are all frozen must stay in eval mode (its running statistics are part of
    the frozen pretrained state and must not drift).
    """
    raise NotImplementedError("TODO: implement PT-11")


def unfreeze(model: nn.Module, optimizer: torch.optim.Optimizer, layer_names: Iterable[str], lr: float) -> None:
    """Make the named backbone layers trainable and let `optimizer` update them at `lr`.

    - Existing groups (learning rates and optimizer state such as momentum) are kept.
    - Newly trainable parameters go into one new parameter group with `lr`; parameters
      the optimizer already owns are never added twice, and no empty group is added.
    - An unknown layer name raises `ValueError`.
    """
    raise NotImplementedError("TODO: implement PT-11")
