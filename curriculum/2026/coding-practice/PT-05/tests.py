from solution import train_with_accumulation

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "train_with_accumulation")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_accumulation_flushes_partial_batch():
    import torch
    model=torch.nn.Linear(1,1); opt=torch.optim.SGD(model.parameters(),lr=.1); scheduler=torch.optim.lr_scheduler.StepLR(opt,1)
    steps=train_with_accumulation(model,[(torch.ones(1,1),torch.ones(1,1))]*3,opt,scheduler,2,1.0); assert steps==2
