import copy

import pytest
import torch
from torch.utils.data import DataLoader

from solution import SequenceDataset, collate_batch, length_bucketed_batches, move_batch_to_device

SEQS = [[5, 0, 7], [], [3], [0, 0, 9, 4, 2], [8, 6]]  # 0 is also the pad id; one empty
LABELS = [1, 0, 2, 1, 0]
IDS = ["a", "b", "c", "d", "e"]


def _ds() -> SequenceDataset:
    return SequenceDataset(SEQS, LABELS, IDS)


def test_implementation_replaces_todo():
    import inspect
    import solution
    for name in ("SequenceDataset", "collate_batch", "move_batch_to_device", "length_bucketed_batches"):
        source = inspect.getsource(getattr(solution, name))
        assert "NotImplementedError" not in source and "TODO: implement" not in source, name


def test_dataset_len_and_items():
    ds = _ds()
    assert len(ds) == 5
    item = ds[3]
    assert item["tokens"].dtype == torch.long and item["tokens"].tolist() == [0, 0, 9, 4, 2]
    assert item["label"] == 1 and item["id"] == "d"
    empty = ds[1]["tokens"]
    assert empty.shape == (0,) and empty.dtype == torch.long
    with pytest.raises(ValueError):
        SequenceDataset(SEQS, LABELS[:4], IDS)
    with pytest.raises(ValueError):
        SequenceDataset(SEQS, LABELS, IDS[:3])


def test_items_do_not_alias_raw_tensor_sequences():
    raw = [torch.tensor([1, 2, 3]), torch.tensor([4])]
    ds = SequenceDataset(raw, [0, 1], ["x", "y"])
    ds[0]["tokens"][0] = 99
    batch = collate_batch([ds[0], ds[1]])
    batch["tokens"][0, 1] = 77
    assert raw[0].tolist() == [1, 2, 3] and ds[0]["tokens"].tolist() == [1, 2, 3]


def test_collate_pads_right_with_mask_from_lengths():
    ds = _ds()
    batch = collate_batch([ds[i] for i in range(5)])
    assert batch["tokens"].shape == (5, 5) and batch["tokens"].dtype == torch.long
    assert batch["tokens"].tolist() == [
        [5, 0, 7, 0, 0],
        [0, 0, 0, 0, 0],
        [3, 0, 0, 0, 0],
        [0, 0, 9, 4, 2],
        [8, 6, 0, 0, 0],
    ]
    assert batch["mask"].dtype == torch.bool
    assert batch["mask"].tolist() == [[j < len(s) for j in range(5)] for s in SEQS]
    assert batch["lengths"].dtype == torch.long and batch["lengths"].tolist() == [3, 0, 1, 5, 2]
    assert batch["labels"].dtype == torch.long and batch["labels"].tolist() == LABELS
    assert batch["ids"] == IDS


def test_collate_custom_pad_value_and_order():
    ds = _ds()
    batch = collate_batch([ds[4], ds[2], ds[0]], pad_value=-1)
    assert batch["tokens"].tolist() == [[8, 6, -1], [3, -1, -1], [5, 0, 7]]
    assert batch["mask"].sum(dim=1).tolist() == [2, 1, 3]
    assert batch["ids"] == ["e", "c", "a"] and batch["labels"].tolist() == [0, 2, 1]


def test_collate_batch_of_one_and_all_empty():
    ds = _ds()
    one = collate_batch([ds[3]])
    assert one["tokens"].shape == (1, 5) and one["mask"].all() and one["lengths"].tolist() == [5]
    empty = collate_batch([ds[1], ds[1]])
    assert empty["tokens"].shape == (2, 0) and empty["mask"].shape == (2, 0)
    assert empty["lengths"].tolist() == [0, 0]


def test_collate_does_not_modify_items():
    ds = _ds()
    items = [ds[i] for i in (0, 3, 1)]
    snapshot = copy.deepcopy(items)
    collate_batch(items, pad_value=-5)
    for got, want in zip(items, snapshot):
        assert torch.equal(got["tokens"], want["tokens"]) and got["label"] == want["label"] and got["id"] == want["id"]


def test_dataloader_integration_preserves_order_and_short_final_batch():
    loader = DataLoader(_ds(), batch_size=2, shuffle=False, collate_fn=collate_batch)
    batches = list(loader)
    assert [b["ids"] for b in batches] == [["a", "b"], ["c", "d"], ["e"]]
    assert [tuple(b["tokens"].shape) for b in batches] == [(2, 3), (2, 5), (1, 2)]


def test_move_batch_to_device_moves_tensors_only():
    batch = collate_batch([_ds()[i] for i in range(3)])
    moved = move_batch_to_device(batch, torch.device("meta"))  # a real non-CPU device on any machine
    assert moved is not batch and set(moved) == set(batch)
    for key in ("tokens", "mask", "lengths", "labels"):
        assert moved[key].device.type == "meta" and moved[key].dtype == batch[key].dtype
        assert moved[key].shape == batch[key].shape and batch[key].device.type == "cpu"
    assert moved["ids"] == ["a", "b", "c"]
    back = move_batch_to_device(batch, "cpu")
    assert torch.equal(back["tokens"], batch["tokens"])


def test_length_bucketed_batches_reduce_padding():
    lengths = [len(s) for s in SEQS]
    batches = length_bucketed_batches(lengths, 2)
    assert batches == [[1, 2], [4, 0], [3]]
    assert sorted(i for b in batches for i in b) == list(range(5))
    loader = DataLoader(_ds(), batch_sampler=batches, collate_fn=collate_batch)
    padded = sum(b["tokens"].numel() for b in loader)
    naive = sum(b["tokens"].numel() for b in DataLoader(_ds(), batch_size=2, collate_fn=collate_batch))
    assert padded < naive
    assert length_bucketed_batches([2, 2, 2], 2) == [[0, 1], [2]]  # ties keep index order
