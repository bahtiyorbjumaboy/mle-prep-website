def batched_inference(model, inputs, batch_size, device):
    """Starting from a correct FP32 training/inference loop, add device-aware autocast and gradient scaling where appropriate, then implement memory-bounded batched inference with `eval()` and inference/no-grad semantics. Collect outputs without retaining graphs.

    Return values must follow the canonical problem contract.
    """
    raise NotImplementedError("TODO: implement PT-10")
