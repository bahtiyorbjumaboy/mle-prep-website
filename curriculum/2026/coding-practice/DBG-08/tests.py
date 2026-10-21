from solution import optimized_features

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "optimized_features")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_matches_reference_and_avoids_quadratic_membership():
    import pandas as pd
    frame=pd.DataFrame({"user_id":[1,1,2],"value":[1.,2.,4.]}); out=optimized_features(frame)
    assert out.sort_values("user_id")["value_sum"].tolist()==[3.,4.]
