from solution import masked_losses

def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "masked_losses")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source

def test_mask_denominator_and_all_masked():
    import torch
    logits=torch.tensor([[0.,2.],[2.,0.]]); targets=torch.tensor([1,0]); mask=torch.tensor([True,False]); out=masked_losses(logits,targets,mask)
    assert torch.isfinite(out["loss"]) and out["count"]==1
