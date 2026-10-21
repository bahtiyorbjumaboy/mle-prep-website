from solution import extend_evaluator

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "extend_evaluator")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_streaming_segment_and_k_metrics():
    records=[{"segment":"a","relevant":{2},"ranked":[1,2,3]},{"segment":"a","relevant":{1},"ranked":[1,4]}]
    out=extend_evaluator(iter(records),ks=(1,2)); assert out["overall"]["recall@2"]==1 and "a" in out["segments"]
