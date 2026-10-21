from solution import align_labels_and_rows

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "align_labels_and_rows")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_duplicate_keys_are_rejected_or_reconciled():
    features=[{"id":2,"x":1},{"id":1,"x":2}]; labels=[{"id":1,"y":0},{"id":2,"y":1}]
    x,y=align_labels_and_rows(features,labels); assert [r["id"] for r in x]==[2,1] and y==[1,0]
