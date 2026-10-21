from typing import Any, Sequence

import torch
from torch.utils.data import Dataset

# Canonical prompt: build a Dataset and custom `collate_fn` for variable-length
# sequences that pads examples, returns masks and labels/metadata, and supports device
# transfer. Follow-ups: empty sequence; sorting/bucketing by length.


class SequenceDataset(Dataset):
    """`dataset[i]` -> `{"tokens": int64 (L_i,), "label": int, "id": str}`.

    - `sequences` are lists of ints or 1-D int tensors (possibly empty); `labels` ints; `ids` strings.
    - Mismatched lengths of `sequences`, `labels`, `ids` raise `ValueError`.
    - Returned tensors must not alias the raw data: editing an item in place must not
      change the dataset.
    """

    def __init__(self, sequences: Sequence[Sequence[int]], labels: Sequence[int], ids: Sequence[str]) -> None:
        raise NotImplementedError("TODO: implement PT-06")

    def __len__(self) -> int:
        raise NotImplementedError("TODO: implement PT-06")

    def __getitem__(self, index: int) -> dict[str, Any]:
        raise NotImplementedError("TODO: implement PT-06")


def collate_batch(items: list[dict[str, Any]], pad_value: int = 0) -> dict[str, Any]:
    """`collate_fn` for `DataLoader`. Keeps item order and returns:

    - `"tokens"`: int64 `(B, L_max)`, right-padded with `pad_value` (`L_max` may be 0);
    - `"mask"`: bool `(B, L_max)`, True at real tokens (`pad_value` may also be a real token);
    - `"lengths"`: int64 `(B,)` original lengths;
    - `"labels"`: int64 `(B,)`;
    - `"ids"`: list of the items' ids.
    Input items must not be modified.
    """
    raise NotImplementedError("TODO: implement PT-06")


def move_batch_to_device(batch: dict[str, Any], device: torch.device | str) -> dict[str, Any]:
    """Return a new dict with every tensor moved to `device`; other values unchanged."""
    raise NotImplementedError("TODO: implement PT-06")


def length_bucketed_batches(lengths: Sequence[int], batch_size: int) -> list[list[int]]:
    """Batches of dataset indices (usable as a `batch_sampler`) grouping similar lengths.

    Sort indices by `(length, index)` ascending, then chunk into `batch_size` (last may be short).
    """
    raise NotImplementedError("TODO: implement PT-06")
