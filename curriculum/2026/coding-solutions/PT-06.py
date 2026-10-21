from typing import Any, Sequence

import torch
from torch.utils.data import Dataset


class SequenceDataset(Dataset):
    """Variable-length token sequences with an int label and a string id each."""

    def __init__(self, sequences: Sequence[Sequence[int]], labels: Sequence[int], ids: Sequence[str]) -> None:
        if not len(sequences) == len(labels) == len(ids):
            raise ValueError("sequences, labels, and ids must have the same length")
        self.sequences = sequences
        self.labels = labels
        self.ids = ids

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, index: int) -> dict[str, Any]:
        # as_tensor may share memory with a tensor input; clone so in-place edits of a
        # batch never reach the raw data.
        tokens = torch.as_tensor(self.sequences[index], dtype=torch.long).clone()  # (L,)
        return {"tokens": tokens, "label": int(self.labels[index]), "id": self.ids[index]}


def collate_batch(items: list[dict[str, Any]], pad_value: int = 0) -> dict[str, Any]:
    lengths = torch.tensor([len(item["tokens"]) for item in items], dtype=torch.long)  # (B,) raw lengths
    max_len = int(lengths.max()) if len(items) else 0
    tokens = torch.full((len(items), max_len), pad_value, dtype=torch.long)  # (B, L_max)
    for row, item in enumerate(items):
        tokens[row, : len(item["tokens"])] = item["tokens"]  # right padding
    # From lengths, not tokens != pad_value: a real token may equal the pad id.
    mask = torch.arange(max_len).unsqueeze(0) < lengths.unsqueeze(1)  # (B, L_max) True = real
    return {
        "tokens": tokens,
        "mask": mask,
        "lengths": lengths,
        "labels": torch.tensor([item["label"] for item in items], dtype=torch.long),  # (B,)
        "ids": [item["id"] for item in items],
    }


def move_batch_to_device(batch: dict[str, Any], device: torch.device | str) -> dict[str, Any]:
    return {key: value.to(device) if isinstance(value, torch.Tensor) else value for key, value in batch.items()}


def length_bucketed_batches(lengths: Sequence[int], batch_size: int) -> list[list[int]]:
    order = sorted(range(len(lengths)), key=lambda i: (lengths[i], i))  # similar lengths share a batch
    return [order[i : i + batch_size] for i in range(0, len(order), batch_size)]
