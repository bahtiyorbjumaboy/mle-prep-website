import copy
from collections import OrderedDict

import pytest
import torch
import torch.nn.functional as F
from torch import nn

from solution import freeze_backbone, make_optimizer, set_train_mode, unfreeze

HEAD_LR, BACKBONE_LR = 0.1, 0.01


class Net(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.backbone = nn.Sequential(
            OrderedDict(
                block1=nn.Sequential(nn.Linear(4, 8), nn.BatchNorm1d(8), nn.ReLU()),
                block2=nn.Sequential(nn.Linear(8, 8), nn.BatchNorm1d(8), nn.ReLU()),
            )
        )
        self.head = nn.Sequential(nn.Dropout(0.2), nn.Linear(8, 3))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.backbone(x))


def _pretrained() -> Net:
    torch.manual_seed(0)
    model = Net()
    model.train()
    with torch.no_grad():
        for _ in range(3):
            model(torch.randn(16, 4) * 2 + 1)  # non-trivial BatchNorm running statistics
    return model


def _batch(seed: int = 1) -> tuple[torch.Tensor, torch.Tensor]:
    g = torch.Generator().manual_seed(seed)
    return torch.randn(12, 4, generator=g), torch.randint(0, 3, (12,), generator=g)


def _step(model: Net, optimizer: torch.optim.Optimizer, seed: int = 1) -> dict[str, torch.Tensor | None]:
    set_train_mode(model)
    x, y = _batch(seed)
    optimizer.zero_grad()
    F.cross_entropy(model(x), y).backward()
    grads = {n: None if p.grad is None else p.grad.clone() for n, p in model.named_parameters()}
    optimizer.step()
    return grads


def _owned(optimizer: torch.optim.Optimizer) -> list[set[int]]:
    return [{id(p) for p in g["params"]} for g in optimizer.param_groups]


def _ids(module: nn.Module) -> set[int]:
    return {id(p) for p in module.parameters()}


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("freeze_backbone", "make_optimizer", "set_train_mode", "unfreeze"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_freeze_sets_requires_grad_and_optimizer_owns_only_head():
    model = _pretrained()
    for p in model.head.parameters():
        p.requires_grad_(False)  # freeze_backbone must also make the head trainable
    freeze_backbone(model)
    assert not any(p.requires_grad for p in model.backbone.parameters())
    assert all(p.requires_grad for p in model.head.parameters())
    opt = make_optimizer(model, HEAD_LR)
    assert isinstance(opt, torch.optim.SGD) and _owned(opt) == [_ids(model.head)]
    assert opt.param_groups[0]["lr"] == HEAD_LR and opt.param_groups[0]["momentum"] == 0.9


def test_frozen_backbone_and_its_batchnorm_stats_do_not_change():
    model = _pretrained()
    freeze_backbone(model)
    opt = make_optimizer(model, HEAD_LR)
    backbone_before = copy.deepcopy(model.backbone.state_dict())  # params AND running stats
    head_before = copy.deepcopy(model.head.state_dict())
    grads = _step(model, opt)
    for k, v in model.backbone.state_dict().items():
        assert torch.equal(v, backbone_before[k]), k
    assert all(grads[n] is None for n in grads if n.startswith("backbone."))
    assert all(grads[n] is not None and torch.isfinite(grads[n]).all() for n in grads if n.startswith("head."))
    assert all(not torch.equal(v, head_before[k]) for k, v in model.head.state_dict().items())


def test_set_train_mode_keeps_only_frozen_batchnorm_in_eval():
    model = _pretrained().eval()
    freeze_backbone(model)
    set_train_mode(model)
    assert model.training and model.head.training and model.head[0].training  # dropout active
    assert model.backbone.block1[0].training  # non-BN layers follow train()
    assert not model.backbone.block1[1].training and not model.backbone.block2[1].training
    opt = make_optimizer(model, HEAD_LR)
    unfreeze(model, opt, ["block2"], BACKBONE_LR)
    set_train_mode(model)
    assert not model.backbone.block1[1].training and model.backbone.block2[1].training


def test_unfreeze_adds_lower_lr_group_and_keeps_head_state():
    model = _pretrained()
    freeze_backbone(model)
    opt = make_optimizer(model, HEAD_LR)
    _step(model, opt)
    head_momentum = {id(p): opt.state[p]["momentum_buffer"].clone() for p in model.head.parameters()}
    unfreeze(model, opt, ["block2"], BACKBONE_LR)
    assert all(p.requires_grad for p in model.backbone.block2.parameters())
    assert not any(p.requires_grad for p in model.backbone.block1.parameters())
    assert _owned(opt) == [_ids(model.head), _ids(model.backbone.block2)]
    assert [g["lr"] for g in opt.param_groups] == [HEAD_LR, BACKBONE_LR]
    for p in model.head.parameters():
        assert torch.equal(opt.state[p]["momentum_buffer"], head_momentum[id(p)])


def test_after_unfreeze_new_params_update_at_their_lr_and_still_frozen_do_not():
    model = _pretrained()
    freeze_backbone(model)
    opt = make_optimizer(model, HEAD_LR)
    _step(model, opt)
    unfreeze(model, opt, ["block2"], BACKBONE_LR)
    before = {n: p.detach().clone() for n, p in model.named_parameters()}
    block1_stats = copy.deepcopy(model.backbone.block1[1].state_dict())
    grads = _step(model, opt, seed=2)
    for n, p in model.named_parameters():
        if n.startswith("backbone.block2."):
            # First step for a fresh SGD-momentum group: buffer = grad, update = -lr * grad.
            assert grads[n] is not None
            assert torch.allclose(p, before[n] - BACKBONE_LR * grads[n], atol=1e-7), n
        elif n.startswith("backbone.block1."):
            assert grads[n] is None and torch.equal(p, before[n]), n
    for k, v in model.backbone.block1[1].state_dict().items():
        assert torch.equal(v, block1_stats[k]), k


def test_unfreeze_is_idempotent_and_validates_names():
    model = _pretrained()
    freeze_backbone(model)
    opt = make_optimizer(model, HEAD_LR)
    unfreeze(model, opt, ["block2"], BACKBONE_LR)
    unfreeze(model, opt, ["block2"], BACKBONE_LR)
    assert len(opt.param_groups) == 2
    unfreeze(model, opt, ["block1.0", "block2"], 0.001)  # only the new Linear joins, in a new group
    assert _owned(opt)[2] == _ids(model.backbone.block1[0]) and opt.param_groups[2]["lr"] == 0.001
    with pytest.raises(ValueError):
        unfreeze(model, opt, ["block9"], BACKBONE_LR)


def test_rebuilt_optimizer_after_full_unfreeze_owns_everything():
    model = _pretrained()
    freeze_backbone(model)
    opt = make_optimizer(model, HEAD_LR)
    unfreeze(model, opt, ["block1", "block2"], BACKBONE_LR)
    assert set().union(*_owned(opt)) == _ids(model)
    fresh = make_optimizer(model, HEAD_LR)  # building from scratch now includes the backbone
    assert _owned(fresh) == [_ids(model)]
