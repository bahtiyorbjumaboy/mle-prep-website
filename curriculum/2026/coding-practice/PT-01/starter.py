import torch
from torch import nn

# Canonical prompt: implement an MLP classifier with one categorical embedding,
# continuous features, two hidden layers, ReLU, dropout, and C-way logits.
# Annotate every intermediate shape (B = batch size) in comments.


class ShapeAwareMLP(nn.Module):
    """Tabular MLP classifier over one categorical id plus continuous features.

    Contract:
    - `__init__(num_categories, embedding_dim, num_continuous, hidden_dims, num_classes,
      dropout=0.1)` where `hidden_dims = (h1, h2)`.
    - Architecture, in order: embed the ids into `embedding_dim`, concatenate the
      embedding with the continuous features, then
      `Linear -> ReLU -> Dropout -> Linear -> ReLU -> Dropout -> Linear(num_classes)`.
      All layers have biases; no other learnable parameters or layers.
    - Every learnable tensor must be registered so it appears in `.parameters()`
      and `.state_dict()`.
    - `forward(category_ids, continuous)` takes `category_ids` int64 `(B,)` and
      `continuous` float `(B, num_continuous)` and returns raw logits `(B, num_classes)`
      (no softmax / log-softmax), including when `B == 1`.
    - Ids outside `[0, num_categories)` raise `ValueError` before any lookup.
    """

    def __init__(
        self,
        num_categories: int,
        embedding_dim: int,
        num_continuous: int,
        hidden_dims: tuple[int, int],
        num_classes: int,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        raise NotImplementedError("TODO: implement PT-01")

    def forward(self, category_ids: torch.Tensor, continuous: torch.Tensor) -> torch.Tensor:
        """Return logits `(B, num_classes)`; annotate each intermediate shape."""
        raise NotImplementedError("TODO: implement PT-01")
