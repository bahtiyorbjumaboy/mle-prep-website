def extend_evaluator(records, ks=(1, 5, 10)):
    """Given a tested ranking evaluator with `add_query`, `compute`, and `reset`, add per-segment metrics, arbitrary `recall@k`, and streaming accumulation where mathematically possible without breaking existing tests.

    Return values must follow the canonical problem contract.
    """
    raise NotImplementedError("TODO: implement DBG-07")
