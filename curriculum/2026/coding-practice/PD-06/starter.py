import pandas as pd


def reshape_and_reconcile(frame: pd.DataFrame, dimension: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Normalize list-valued rows, map them through a multi-key dimension, pivot, and reconcile.

    Args:
        frame: columns entity_id, region, codes (a list of code strings, possibly empty, or
            missing), value (float).
        dimension: columns region, code, label. (region, code) must be unique; raise
            ValueError otherwise. The same code can map to different labels in different regions.

    Allocation rules:
        - A row's value is split equally across the entries of its codes list; a code listed
          twice receives two shares.
        - A row with an empty or missing codes list allocates its whole value to the label
          'unassigned'.
        - A (region, code) pair missing from `dimension` maps to the label 'unknown'.

    Returns:
        (wide, reconciliation)
        wide: one row per entity_id, sorted, fresh RangeIndex, columns: entity_id, one column
            per label that receives any allocation (sorted alphabetically) holding the
            allocated value (0.0 where none), then total (sum of the label columns) and n_codes
            (number of list entries across the entity's rows).
        reconciliation: {"before": total value in `frame`, "after": total across all label
            columns of `wide`, "difference": after - before, "balanced": |difference| <= 1e-9}.
        The inputs must not be modified.
    """
    raise NotImplementedError("TODO: implement PD-06")
