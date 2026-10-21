import torch
from torch import nn

# Canonical prompt: implement a compact image classifier using convolution, activation,
# pooling, adaptive pooling, and a linear head. Annotate output shapes and parameter
# counts after every learned layer.
# Follow-ups: arbitrary image size; BatchNorm train/eval behavior; replace pooling with stride.


def conv2d_output_size(size: int, kernel: int, stride: int = 1, padding: int = 0, dilation: int = 1) -> int:
    """Output length of one spatial axis for `nn.Conv2d` / `nn.MaxPool2d` with these settings."""
    raise NotImplementedError("TODO: implement PT-09")


def conv2d_param_count(in_channels: int, out_channels: int, kernel: int, bias: bool = True) -> int:
    """Learnable parameters of a square-kernel `nn.Conv2d` (groups=1)."""
    raise NotImplementedError("TODO: implement PT-09")


class CompactCNN(nn.Module):
    """NCHW classifier; input `(N, in_channels, H, W)` with any `N >= 1`, `H, W >= 2`.

    Architecture (attribute names are part of the contract), `channels = (c1, c2)`:
    - `conv1`: 3x3 conv, padding 1, `in_channels -> c1`; then `bn1` if `batchnorm`
      else no normalisation; ReLU; 2x2 max pool (stride 2);
    - `conv2`: 3x3 conv, padding 1, `c1 -> c2`; then `bn2` if `batchnorm`; ReLU;
    - global adaptive average pool to 1x1, flatten to `(N, c2)`;
    - `head`: `Linear(c2, num_classes)` returning raw logits `(N, num_classes)`.
    With `batchnorm=True` the convs have no bias (BatchNorm's shift makes it redundant).
    """

    def __init__(
        self, in_channels: int, num_classes: int, channels: tuple[int, int] = (16, 32), batchnorm: bool = False
    ) -> None:
        super().__init__()
        raise NotImplementedError("TODO: implement PT-09")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError("TODO: implement PT-09")


def predicted_shapes(
    in_channels: int, num_classes: int, channels: tuple[int, int], height: int, width: int
) -> dict[str, tuple[int, ...]]:
    """Per-sample output shapes (batch axis omitted), computed from the formulas, not by
    running the model: keys `"conv1"`, `"pool"`, `"conv2"`, `"gap"` (flattened), `"logits"`.
    """
    raise NotImplementedError("TODO: implement PT-09")


def predicted_param_counts(
    in_channels: int, num_classes: int, channels: tuple[int, int], batchnorm: bool = False
) -> dict[str, int]:
    """Learnable parameters per learned layer: `"conv1"`, `"conv2"`, `"head"`, plus
    `"bn1"`, `"bn2"` when `batchnorm` (running statistics are buffers, not parameters).
    """
    raise NotImplementedError("TODO: implement PT-09")
