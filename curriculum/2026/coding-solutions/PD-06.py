import numpy as np
import pandas as pd


def reshape_and_reconcile(frame: pd.DataFrame, dimension: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Explode, map through (region, code), pivot labels, and check value conservation."""
    if dimension.duplicated(["region", "code"]).any():
        raise ValueError("dimension must be unique on (region, code)")
    rows = frame.assign(
        codes=frame["codes"].map(lambda codes: list(codes) if isinstance(codes, (list, tuple, np.ndarray)) else []),
    )
    rows["n_codes"] = rows["codes"].map(len)
    # Split before exploding so each exploded row carries its share, not the full value.
    rows["share"] = rows["value"] / rows["n_codes"].where(rows["n_codes"] > 0, 1)
    exploded = rows.explode("codes").rename(columns={"codes": "code"})

    mapped = exploded.merge(dimension, on=["region", "code"], how="left", validate="many_to_one")
    mapped["label"] = np.where(mapped["code"].isna(), "unassigned", mapped["label"].fillna("unknown"))

    wide = mapped.pivot_table(index="entity_id", columns="label", values="share", aggfunc="sum", fill_value=0.0)
    wide = wide[sorted(wide.columns)]
    wide.columns.name = None
    wide["total"] = wide.sum(axis=1)
    wide["n_codes"] = rows.groupby("entity_id")["n_codes"].sum()
    wide = wide.reset_index()

    before = float(frame["value"].sum())
    after = float(wide.drop(columns=["entity_id", "total", "n_codes"]).to_numpy().sum())
    reconciliation = {"before": before, "after": after, "difference": after - before,
                      "balanced": abs(after - before) <= 1e-9}
    return wide, reconciliation
