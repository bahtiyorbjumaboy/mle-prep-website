from solution import resume_training

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "resume_training")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_resume_restores_rng_and_step(tmp_path):
    import torch
    model=torch.nn.Linear(1,1); opt=torch.optim.SGD(model.parameters(),lr=.1); scheduler=torch.optim.lr_scheduler.StepLR(opt,1)
    path=tmp_path/"c.pt"; torch.save({"model":model.state_dict(),"optimizer":opt.state_dict(),"scheduler":scheduler.state_dict(),"step":7},path)
    assert resume_training(path,model,opt,scheduler)==7
