import pytest
import torch
from torch import nn

from solution import (
    CompactCNN,
    conv2d_output_size,
    conv2d_param_count,
    predicted_param_counts,
    predicted_shapes,
)


def _model(batchnorm: bool = False, seed: int = 0) -> CompactCNN:
    torch.manual_seed(seed)
    return CompactCNN(in_channels=3, num_classes=5, channels=(6, 10), batchnorm=batchnorm)


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("conv2d_output_size", "conv2d_param_count", "CompactCNN", "predicted_shapes", "predicted_param_counts"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


@pytest.mark.parametrize(
    "size,kernel,stride,padding,dilation",
    [(32, 3, 1, 1, 1), (17, 3, 2, 1, 1), (17, 5, 2, 0, 1), (10, 3, 1, 0, 2), (7, 2, 2, 0, 1), (9, 4, 3, 2, 1), (5, 5, 1, 0, 1)],
)
def test_conv_output_size_matches_pytorch(size, kernel, stride, padding, dilation):
    conv = nn.Conv2d(1, 1, kernel, stride=stride, padding=padding, dilation=dilation)
    actual = conv(torch.zeros(1, 1, size, size + 3)).shape
    assert conv2d_output_size(size, kernel, stride, padding, dilation) == actual[2]
    assert conv2d_output_size(size + 3, kernel, stride, padding, dilation) == actual[3]


@pytest.mark.parametrize("cin,cout,k,bias", [(3, 16, 3, True), (16, 32, 5, False), (1, 1, 1, True), (7, 4, 2, False)])
def test_conv_param_count_matches_pytorch(cin, cout, k, bias):
    conv = nn.Conv2d(cin, cout, k, bias=bias)
    assert conv2d_param_count(cin, cout, k, bias) == sum(p.numel() for p in conv.parameters())


@pytest.mark.parametrize("n,h,w", [(1, 2, 2), (2, 32, 32), (3, 17, 30), (4, 9, 5)])
def test_logits_shape_for_any_batch_and_image_size(n, h, w):
    model = _model().eval()
    out = model(torch.randn(n, 3, h, w))
    assert out.shape == (n, 5)


def test_layer_shapes_match_prediction_via_hooks():
    model = _model().eval()
    seen = {}

    def record(name, use_input):
        def hook(module, inputs, output=None):
            seen[name] = tuple((inputs[0] if use_input else output).shape[1:])  # returns None: observe only

        return hook

    model.conv1.register_forward_hook(record("conv1", False))
    model.conv2.register_forward_pre_hook(record("pool", True))
    model.conv2.register_forward_hook(record("conv2", False))
    model.head.register_forward_pre_hook(record("gap", True))
    out = model(torch.randn(2, 3, 13, 22))
    seen["logits"] = tuple(out.shape[1:])
    want = predicted_shapes(3, 5, (6, 10), 13, 22)
    assert seen == want
    assert want == {"conv1": (6, 13, 22), "pool": (6, 6, 11), "conv2": (10, 6, 11), "gap": (10,), "logits": (5,)}


@pytest.mark.parametrize("batchnorm", [False, True])
def test_parameter_accounting(batchnorm):
    model = _model(batchnorm=batchnorm)
    counts = predicted_param_counts(3, 5, (6, 10), batchnorm=batchnorm)
    for name, count in counts.items():
        assert sum(p.numel() for p in getattr(model, name).parameters()) == count, name
    assert sum(p.numel() for p in model.parameters()) == sum(counts.values())
    if batchnorm:
        assert counts == {"conv1": 162, "conv2": 540, "head": 55, "bn1": 12, "bn2": 20}
        assert model.conv1.bias is None and model.conv2.bias is None
    else:
        assert counts == {"conv1": 168, "conv2": 550, "head": 55}


def test_architecture_contract():
    model = _model()
    assert isinstance(model.conv1, nn.Conv2d) and model.conv1.kernel_size == (3, 3) and model.conv1.padding == (1, 1)
    assert (model.conv1.in_channels, model.conv1.out_channels) == (3, 6)
    assert (model.conv2.in_channels, model.conv2.out_channels) == (6, 10)
    assert isinstance(model.head, nn.Linear) and (model.head.in_features, model.head.out_features) == (10, 5)
    assert any(isinstance(m, nn.MaxPool2d) for m in model.modules())
    assert any(isinstance(m, nn.AdaptiveAvgPool2d) for m in model.modules())


def test_head_sees_global_average_of_conv2_activations():
    model = _model().eval()
    seen = {}
    model.conv2.register_forward_hook(lambda m, i, o: seen.update(conv2=o))
    model.head.register_forward_pre_hook(lambda m, i: seen.update(head_in=i[0]))
    model(torch.randn(3, 3, 11, 14))
    assert torch.allclose(seen["head_in"], torch.relu(seen["conv2"]).mean(dim=(2, 3)), atol=1e-6)


def test_channels_first_and_raw_logits():
    model = _model().eval()
    final = {}
    model.head.register_forward_hook(lambda m, i, o: final.update(out=o))
    x = torch.randn(2, 3, 8, 12)
    out = model(x)
    assert torch.equal(out, final["out"])
    with pytest.raises(RuntimeError):
        model(x.permute(0, 2, 3, 1))  # NHWC input must not be silently accepted


def test_samples_are_independent_in_eval_and_gradients_flow():
    model = _model(batchnorm=True)
    model.train()
    model(torch.randn(8, 3, 10, 10))  # update running stats
    model.eval()
    x = torch.randn(4, 3, 10, 11)
    full = model(x)
    assert torch.allclose(model(x[2:3]), full[2:3], atol=1e-6)  # eval BN uses running stats
    model.train()
    assert not torch.allclose(model(x[2:3].repeat(2, 1, 1, 1))[0], model(x)[2], atol=1e-4)  # train BN uses batch stats
    model.zero_grad()
    nn.functional.cross_entropy(model(x), torch.tensor([0, 1, 2, 3])).backward()
    for name, p in model.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all(), name
