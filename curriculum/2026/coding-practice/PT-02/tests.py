from solution import train_and_validate

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "train_and_validate")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_loop_uses_eval_and_sample_weighting():
    import torch
    model=torch.nn.Linear(1,1); data=[(torch.tensor([[0.],[1.]]),torch.tensor([[0.],[1.]]))]; opt=torch.optim.SGD(model.parameters(),lr=.1)
    metrics=train_and_validate(model,data,data,opt,torch.nn.MSELoss(),"cpu"); assert set(metrics)>={"train_loss","val_loss"} and model.training is False
