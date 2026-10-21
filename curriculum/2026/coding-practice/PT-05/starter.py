def train_with_accumulation(model, loader, optimizer, scheduler, accumulation_steps, max_grad_norm):
    """Modify a training loop to emulate a larger batch with microbatches, add global-norm clipping, and apply warmup + cosine scheduling at the correct cadence.

    Return values must follow the canonical problem contract.
    """
    raise NotImplementedError("TODO: implement PT-05")
