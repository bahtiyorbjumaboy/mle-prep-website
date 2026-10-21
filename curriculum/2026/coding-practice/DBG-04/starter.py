def stable_numerical_pipeline(values):
    """A training loss becomes NaN. Instrument the computation to identify the first non-finite tensor among unstable softmax, `log(0)`, zero-norm normalization, and an excessive learning rate. Fix the root cause and add regression tests.

    Return values must follow the canonical problem contract.
    """
    raise NotImplementedError("TODO: implement DBG-04")
