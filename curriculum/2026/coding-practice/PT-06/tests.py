from solution import SequenceDataset

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "SequenceDataset")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_collate_padding_and_lengths():
    import torch
    dataset=SequenceDataset([torch.ones(2,3),torch.ones(1,3)],[0,1]); batch=dataset.collate_fn([dataset[0],dataset[1]])
    assert batch["x"].shape==(2,2,3) and batch["lengths"].tolist()==[2,1]
