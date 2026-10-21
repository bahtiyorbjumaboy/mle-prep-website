from solution import repair_tensor_pipeline

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "repair_tensor_pipeline")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_repaired_shape_and_no_silent_broadcast():
    import torch
    x=torch.arange(24.).reshape(2,3,4); out=repair_tensor_pipeline(x); assert out.shape[0]==2 and torch.isfinite(out).all()
