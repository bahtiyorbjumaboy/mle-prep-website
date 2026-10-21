def repair_torch_lifecycle(model, batch, optimizer):
    """A PyTorch train/eval script has poor validation, growing GPU memory, and occasional device errors. Find lifecycle bugs involving `eval`, `no_grad`, graph retention, gradient zeroing, and device placement.

    Return values must follow the canonical problem contract.
    """
    raise NotImplementedError("TODO: implement DBG-05")
