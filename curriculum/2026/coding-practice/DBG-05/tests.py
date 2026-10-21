from solution import repair_torch_lifecycle

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "repair_torch_lifecycle")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_lifecycle_returns_detached_metrics():
    import torch
    model=torch.nn.Linear(2,1); optimizer=torch.optim.SGD(model.parameters(),lr=.1); batch=(torch.ones(2,2),torch.ones(2,1))
    result=repair_torch_lifecycle(model,batch,optimizer); assert isinstance(result["loss"],float) and all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters())
