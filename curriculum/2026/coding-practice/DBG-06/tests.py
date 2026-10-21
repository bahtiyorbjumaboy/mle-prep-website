from solution import evaluate_predictions

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "evaluate_predictions")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_denominators_and_single_class():
    import numpy as np
    out=evaluate_predictions(np.array([1,1]),np.array([1,0])); assert out["accuracy"]==.5 and out["recall"]==.5
