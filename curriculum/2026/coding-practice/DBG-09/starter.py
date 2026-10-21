def parity_check(training_path, serving_path, request):
    """Offline predictions match expected metrics, but a serving path produces shifted scores. Given training preprocessing, serialized transformer state, model weights, and online feature code, localize one preprocessing mismatch, one stale-version mismatch, and one dtype/device/numerical discrepancy. Add parity tests that catch the first divergence.

    Return values must follow the canonical problem contract.
    """
    raise NotImplementedError("TODO: implement DBG-09")
