def fit_leakage_safe_pipeline(train, validation):
    """You receive a training pipeline with suspiciously high validation performance. Find and fix three leaks: preprocessing fit before the split, target encoding that sees the row's own target, and a recency feature computed with future information. Write tests that expose each leak.

    Return values must follow the canonical problem contract.
    """
    raise NotImplementedError("TODO: implement DBG-01")
