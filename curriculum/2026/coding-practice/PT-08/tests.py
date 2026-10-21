from solution import scaled_dot_product_attention

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "scaled_dot_product_attention")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_causal_and_padding_masks():
    import torch
    q=k=v=torch.ones(1,1,3,2); out,w=scaled_dot_product_attention(q,k,v,causal=True); assert out.shape==q.shape and torch.all(w[...,0,1:]==0) and torch.allclose(w.sum(-1),torch.ones_like(w.sum(-1)))
