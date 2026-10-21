from solution import stable_numerical_pipeline

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "stable_numerical_pipeline")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_extreme_values_are_finite():
    import numpy as np
    out=stable_numerical_pipeline(np.array([-1000.,0.,1000.])); assert np.isfinite(out).all()
