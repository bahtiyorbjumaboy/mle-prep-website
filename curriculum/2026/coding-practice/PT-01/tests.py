from solution import ShapeAwareMLP

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "ShapeAwareMLP")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_module_shapes_and_parameters():
    import torch
    model=ShapeAwareMLP(4,8,2); out=model(torch.ones(3,4)); assert out.shape==(3,2) and all(p.device==out.device for p in model.parameters())
