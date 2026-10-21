def configure_transfer_learning(model, unfreeze=False):
    """Given a pretrained backbone and new head, freeze the backbone, train only the head, then unfreeze selected layers with a lower learning rate via optimizer parameter groups. Verify which parameters receive gradients and optimizer updates.

    Return values must follow the canonical problem contract.
    """
    raise NotImplementedError("TODO: implement PT-11")
