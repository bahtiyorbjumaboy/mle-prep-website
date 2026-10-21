import numpy as np


def repair_broadcasting(x, scale, mask):
    """Select rows with mask, then scale features without adding an accidental axis."""
    x = np.asarray(x)
    scale = np.asarray(scale)
    mask = np.asarray(mask, dtype=bool)
    if x.ndim != 2 or scale.shape != (x.shape[1],) or mask.shape != (x.shape[0],):
        raise ValueError("expected x=(rows, features), scale=(features,), mask=(rows,)")
    return x[mask] * scale[None, :]
