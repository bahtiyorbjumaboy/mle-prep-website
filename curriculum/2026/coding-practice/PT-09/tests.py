from solution import CompactCNN

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "CompactCNN")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_cnn_arbitrary_image_size():
    import torch
    model=CompactCNN(in_channels=3,num_classes=5); assert model(torch.ones(2,3,32,40)).shape==(2,5)
