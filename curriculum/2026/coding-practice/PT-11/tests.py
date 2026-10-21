from solution import configure_transfer_learning

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "configure_transfer_learning")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_freeze_and_optimizer_groups():
    import torch
    class Model(torch.nn.Module):
        def __init__(self): super().__init__(); self.backbone=torch.nn.Linear(2,2); self.head=torch.nn.Linear(2,1)
    model=Model(); optimizer=configure_transfer_learning(model,unfreeze=False); assert not any(p.requires_grad for p in model.backbone.parameters()) and all(p.requires_grad for p in model.head.parameters()) and len(optimizer.param_groups)==1
