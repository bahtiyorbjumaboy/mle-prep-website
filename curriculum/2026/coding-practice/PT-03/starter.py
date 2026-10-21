def masked_losses(logits, targets, mask):
    """Compute CE using `F.cross_entropy`, `log_softmax+nll_loss`, and a manual logsumexp implementation; then compute masked sequence loss using both ignore-index and explicit masks.

    Return values must follow the canonical problem contract.
    """
    raise NotImplementedError("TODO: implement PT-03")
