from solution import parity_check

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "parity_check")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_golden_request_reports_first_divergence():
    training={"version":"v1","dtype":"float32"}; serving={"version":"v1","dtype":"float32"}; request={"x":[1.,2.]}
    out=parity_check(training,serving,request); assert out["matches"] is True and out["first_divergence"] is None
