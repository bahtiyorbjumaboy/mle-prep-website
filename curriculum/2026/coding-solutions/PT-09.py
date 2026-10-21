import torch
from torch import nn


def conv2d_output_size(size: int, kernel: int, stride: int = 1, padding: int = 0, dilation: int = 1) -> int:
    return (size + 2 * padding - dilation * (kernel - 1) - 1) // stride + 1


def conv2d_param_count(in_channels: int, out_channels: int, kernel: int, bias: bool = True) -> int:
    return out_channels * in_channels * kernel * kernel + (out_channels if bias else 0)


class CompactCNN(nn.Module):
    def __init__(
        self, in_channels: int, num_classes: int, channels: tuple[int, int] = (16, 32), batchnorm: bool = False
    ) -> None:
        super().__init__()
        c1, c2 = channels
        # BatchNorm's beta makes a conv bias redundant.
        self.conv1 = nn.Conv2d(in_channels, c1, kernel_size=3, padding=1, bias=not batchnorm)  # c1*in*9 (+c1)
        self.bn1 = nn.BatchNorm2d(c1) if batchnorm else nn.Identity()  # 2*c1 params, 2*c1 buffers
        self.pool = nn.MaxPool2d(2)
        self.conv2 = nn.Conv2d(c1, c2, kernel_size=3, padding=1, bias=not batchnorm)  # c2*c1*9 (+c2)
        self.bn2 = nn.BatchNorm2d(c2) if batchnorm else nn.Identity()
        self.gap = nn.AdaptiveAvgPool2d(1)  # any H, W -> 1x1, so the head never depends on image size
        self.head = nn.Linear(c2, num_classes)  # num_classes*c2 + num_classes

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool(torch.relu(self.bn1(self.conv1(x))))  # (N, c1, H, W) -> (N, c1, H//2, W//2)
        x = torch.relu(self.bn2(self.conv2(x)))  # (N, c2, H//2, W//2)
        x = self.gap(x).flatten(start_dim=1)  # (N, c2, 1, 1) -> (N, c2); keeps N even when N == 1
        return self.head(x)  # (N, num_classes) logits


def predicted_shapes(
    in_channels: int, num_classes: int, channels: tuple[int, int], height: int, width: int
) -> dict[str, tuple[int, ...]]:
    c1, c2 = channels
    h, w = conv2d_output_size(height, 3, padding=1), conv2d_output_size(width, 3, padding=1)  # same size
    ph, pw = conv2d_output_size(h, 2, stride=2), conv2d_output_size(w, 2, stride=2)  # pooling: same formula
    return {
        "conv1": (c1, h, w),
        "pool": (c1, ph, pw),
        "conv2": (c2, conv2d_output_size(ph, 3, padding=1), conv2d_output_size(pw, 3, padding=1)),
        "gap": (c2,),
        "logits": (num_classes,),
    }


def predicted_param_counts(
    in_channels: int, num_classes: int, channels: tuple[int, int], batchnorm: bool = False
) -> dict[str, int]:
    c1, c2 = channels
    counts = {
        "conv1": conv2d_param_count(in_channels, c1, 3, bias=not batchnorm),
        "conv2": conv2d_param_count(c1, c2, 3, bias=not batchnorm),
        "head": num_classes * c2 + num_classes,
    }
    if batchnorm:
        counts.update(bn1=2 * c1, bn2=2 * c2)
    return counts
