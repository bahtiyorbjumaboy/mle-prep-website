def repair_broadcasting(x, scale, mask):
    """A NumPy scoring function returns plausible but wrong results because softmax uses the wrong axis, row weights broadcast along the wrong dimension, and a global mean collapses structure. Find, fix, and test all three.

    Return values must follow the canonical problem contract.
    """
    raise NotImplementedError("TODO: implement DBG-03")
