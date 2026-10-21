from solution import batched_inference

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "batched_inference")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_batched_inference_is_detached_and_eval():
    import torch
    model=torch.nn.Sequential(torch.nn.Dropout(),torch.nn.Linear(2,1)); out=batched_inference(model,torch.ones(5,2),2,"cpu")
    assert out.shape==(5,1) and not out.requires_grad and model.training is False
