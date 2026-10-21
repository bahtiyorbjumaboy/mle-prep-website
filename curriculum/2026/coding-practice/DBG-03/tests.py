from solution import repair_broadcasting

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "repair_broadcasting")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_basic():
    import numpy as np
    out=repair_broadcasting(np.ones((2,3)),np.array([1,2,3]),np.array([True,False]))
    assert out.shape==(1,3) and out.tolist()==[[1,2,3]]
