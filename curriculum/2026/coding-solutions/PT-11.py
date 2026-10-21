from typing import Iterable

import torch
from torch import nn


def freeze_backbone(model: nn.Module) -> None:
    for p in model.backbone.parameters():
        p.requires_grad_(False)  # no grads computed or stored for these
    for p in model.head.parameters():
        p.requires_grad_(True)


def make_optimizer(model: nn.Module, head_lr: float, momentum: float = 0.9) -> torch.optim.SGD:
    # Own only trainable parameters; frozen ones would just sit in the optimizer, and any
    # weight decay or momentum applied to them would silently move "frozen" weights.
    trainable = [p for p in model.parameters() if p.requires_grad]
    return torch.optim.SGD([{"params": trainable, "lr": head_lr}], lr=head_lr, momentum=momentum)


def set_train_mode(model: nn.Module) -> None:
    model.train()
    for module in model.modules():
        params = list(module.parameters(recurse=False))
        if isinstance(module, nn.modules.batchnorm._BatchNorm) and params and not any(p.requires_grad for p in params):
            # requires_grad does not stop running-stat updates; eval() does.
            module.eval()


def unfreeze(model: nn.Module, optimizer: torch.optim.Optimizer, layer_names: Iterable[str], lr: float) -> None:
    owned = {id(p) for group in optimizer.param_groups for p in group["params"]}
    new_params = []
    for name in layer_names:
        try:
            layer = model.backbone.get_submodule(name)
        except AttributeError as error:
            raise ValueError(f"unknown backbone layer {name!r}") from error
        for p in layer.parameters():
            p.requires_grad_(True)
            if id(p) not in owned:
                owned.add(id(p))
                new_params.append(p)
    if new_params:
        # Extending (not rebuilding) keeps the head's momentum buffers and its own lr.
        optimizer.add_param_group({"params": new_params, "lr": lr})
