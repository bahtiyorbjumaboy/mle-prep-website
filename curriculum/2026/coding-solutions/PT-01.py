import torch
from torch import nn


class ShapeAwareMLP(nn.Module):
    """Embedding + continuous features -> two ReLU/dropout hidden layers -> logits."""

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
        h1, h2 = hidden_dims
        self.num_categories = num_categories
        self.embedding = nn.Embedding(num_categories, embedding_dim)
        self.net = nn.Sequential(
            nn.Linear(embedding_dim + num_continuous, h1),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(h1, h2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(h2, num_classes),
        )

    def forward(self, category_ids: torch.Tensor, continuous: torch.Tensor) -> torch.Tensor:
        # category_ids: (B,) int64; continuous: (B, F)
        if category_ids.numel() and (
            int(category_ids.min()) < 0 or int(category_ids.max()) >= self.num_categories
        ):
            raise ValueError(f"category ids must lie in [0, {self.num_categories})")
        embedded = self.embedding(category_ids)  # (B, E)
        features = torch.cat([embedded, continuous], dim=1)  # (B, E + F)
        # Linear -> (B, h1) -> Linear -> (B, h2) -> Linear -> (B, C); ReLU/Dropout keep shape.
        return self.net(features)  # (B, C) raw logits; CE applies log-softmax itself
