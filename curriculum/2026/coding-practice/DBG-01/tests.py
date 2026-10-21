from solution import fit_leakage_safe_pipeline

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "fit_leakage_safe_pipeline")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_scaler_fits_train_only():
    train={"x":[[0.],[2.]],"y":[0,1]}; validation={"x":[[100.]],"y":[1]}; out=fit_leakage_safe_pipeline(train,validation)
    assert out["scaler_mean"]==[1.] and out["validation_x"][0][0]>10
