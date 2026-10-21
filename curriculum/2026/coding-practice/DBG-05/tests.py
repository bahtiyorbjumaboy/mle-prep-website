import copy
import gc
import math
import weakref

import pytest
import torch
from torch import nn

from solution import evaluate, fit, train_one_epoch, train_step

CPU = torch.device("cpu")


def _data(n=96, seed=0):
    g = torch.Generator().manual_seed(seed)
    x = torch.randn(n, 4, generator=g)
    y = (x[:, 0] + 0.5 * x[:, 1] > 0).long()
    return x, y


def _batches(x, y, size=16):
    return [(x[i : i + size], y[i : i + size]) for i in range(0, len(x), size)]


def _mlp(seed=0, dropout=0.0, batchnorm=False):
    torch.manual_seed(seed)
    layers = [nn.Linear(4, 16)] + ([nn.BatchNorm1d(16)] if batchnorm else [])
    layers += [nn.ReLU(), nn.Dropout(dropout), nn.Linear(16, 2)]
    return nn.Sequential(*layers)


def test_train_step_places_every_tensor_on_the_model_device():
    # `meta` stands in for an accelerator: mixing it with CPU tensors raises the same
    # "Expected all tensors to be on the same device" error a GPU run would.
    device = torch.device("meta")
    model = _mlp().to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    x, y = _data(16)
    loss = train_step(model, (x, y), optimizer, nn.CrossEntropyLoss(), device)
    assert loss.device.type == "meta" and loss.dim() == 0


def test_each_update_uses_only_the_current_batch_gradient():
    model, loss_fn = _mlp(1), nn.CrossEntropyLoss()
    reference = copy.deepcopy(model)
    batches = _batches(*_data())
    mean_loss = train_one_epoch(
        model, batches, torch.optim.SGD(model.parameters(), lr=0.1), loss_fn, CPU
    )

    ref_opt, ref_losses = torch.optim.SGD(reference.parameters(), lr=0.1), []
    reference.train()
    for x, y in batches:  # independent reference loop
        ref_opt.zero_grad()
        loss = loss_fn(reference(x), y)
        loss.backward()
        ref_opt.step()
        ref_losses.append(loss.item())
    for p, q in zip(model.parameters(), reference.parameters()):
        assert torch.allclose(p, q, atol=1e-6), "parameters diverged from per-batch SGD"
    assert isinstance(mean_loss, float)
    assert math.isclose(mean_loss, sum(ref_losses) / len(ref_losses), rel_tol=1e-5)


class _Probe:
    pass


def test_training_does_not_keep_earlier_graphs_alive():
    model = _mlp(2)
    probes, alive_at_forward = [], []

    def hook(module, inputs, output):
        gc.collect()
        alive_at_forward.append(sum(ref() is not None for ref in probes))
        probe = _Probe()
        output.grad_fn.metadata["probe"] = probe  # lives exactly as long as the graph node
        probes.append(weakref.ref(probe))

    model.register_forward_hook(hook)
    batches = _batches(*_data(), size=12)
    train_one_epoch(model, batches, torch.optim.SGD(model.parameters(), lr=0.1), nn.CrossEntropyLoss(), CPU)
    gc.collect()
    assert len(alive_at_forward) == len(batches)
    assert max(alive_at_forward) <= 1, f"live graphs from earlier steps: {alive_at_forward}"
    assert sum(ref() is not None for ref in probes) == 0, "a graph outlived the epoch"


def test_training_still_learns_through_the_full_graph():
    model = _mlp(3)
    before = [p.detach().clone() for p in model.parameters()]
    batches = _batches(*_data())
    opt = torch.optim.SGD(model.parameters(), lr=0.5)
    first = train_one_epoch(model, batches, opt, nn.CrossEntropyLoss(), CPU)
    for _ in range(5):
        last = train_one_epoch(model, batches, opt, nn.CrossEntropyLoss(), CPU)
    assert all(not torch.equal(b, p) for b, p in zip(before, model.parameters())), "a layer never updated"
    assert last < 0.6 * first


def _trained_bn_dropout_model():
    model = _mlp(4, dropout=0.5, batchnorm=True)
    batches = _batches(*_data(seed=1))
    train_one_epoch(model, batches, torch.optim.SGD(model.parameters(), lr=0.1), nn.CrossEntropyLoss(), CPU)
    return model


def test_evaluate_uses_inference_behaviour_and_changes_no_state():
    model = _trained_bn_dropout_model()
    snapshot = copy.deepcopy(model.state_dict())
    val = _batches(*_data(n=50, seed=7), size=8)  # uneven final batch
    first = evaluate(model, val, nn.CrossEntropyLoss(), CPU)
    second = evaluate(model, val, nn.CrossEntropyLoss(), CPU)
    assert first == second, "evaluation must be deterministic"
    for key, value in model.state_dict().items():
        assert torch.equal(value, snapshot[key]), f"evaluation changed {key}"

    reference = copy.deepcopy(model).eval()
    x, y = _data(n=50, seed=7)
    with torch.no_grad():
        logits = reference(x)
        loss = nn.functional.cross_entropy(logits, y).item()
        accuracy = int((logits.argmax(dim=1) == y).sum()) / len(y)
    assert math.isclose(first["loss"], loss, rel_tol=1e-5), (first["loss"], loss)
    assert math.isclose(first["accuracy"], accuracy, rel_tol=1e-9)


def test_evaluate_builds_no_autograd_graph():
    model = _trained_bn_dropout_model()
    flags = []
    model.register_forward_hook(lambda m, i, out: flags.append(out.requires_grad))
    result = evaluate(model, _batches(*_data(n=40, seed=8), size=8), nn.CrossEntropyLoss(), CPU)
    assert flags and not any(flags), "validation forward passes recorded a graph"
    assert all(isinstance(v, float) for v in result.values())


def test_fit_alternates_train_and_eval_modes():
    model = _mlp(5, dropout=0.3)
    modes = []
    model.register_forward_hook(lambda m, i, out: modes.append(m.training))
    train, val = _batches(*_data()), _batches(*_data(n=32, seed=9))
    history = fit(model, train, val, torch.optim.SGD(model.parameters(), lr=0.3), nn.CrossEntropyLoss(), 2, CPU)
    expected = ([True] * len(train) + [False] * len(val)) * 2
    assert modes == expected
    assert len(history) == 2


def test_fit_learns_and_reports_floats():
    model = _mlp(6, dropout=0.2, batchnorm=True)
    train, val = _batches(*_data(n=192, seed=2)), _batches(*_data(n=64, seed=3))
    history = fit(model, train, val, torch.optim.SGD(model.parameters(), lr=0.3), nn.CrossEntropyLoss(), 8, CPU)
    assert all(isinstance(v, float) for row in history for v in row.values())
    assert history[-1]["val_accuracy"] >= 0.9, history[-1]
    assert history[-1]["train_loss"] < history[0]["train_loss"]


@pytest.mark.skipif(not torch.cuda.is_available(), reason="needs a CUDA device")
def test_fit_on_cuda_end_to_end():
    model = _mlp(7, dropout=0.2, batchnorm=True)
    train, val = _batches(*_data()), _batches(*_data(n=32, seed=4))
    history = fit(model, train, val, torch.optim.SGD(model.parameters(), lr=0.3), nn.CrossEntropyLoss(), 2, torch.device("cuda"))
    assert len(history) == 2
