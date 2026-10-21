from typing import Any, Mapping, Sequence


class FeatureTransformer:
    """Stateful preprocessing: numeric standardization/imputation/missing flags plus
    categorical one-hot encoding with an unknown bucket.

    Missing values are absent keys, `None`, or float NaN. Extra keys are ignored.

    Fitted state (learned only in `fit`; a second `fit` replaces all previous state):
        * numeric column: mean and population standard deviation (ddof=0) of its
          non-missing values. If no values are present, use mean 0; if the std is 0 (or
          no values are present), use scale 1.
        * categorical column: the sorted set of non-missing values seen.

    Output layout (`feature_names_`), numeric columns first in constructor order, then
    categorical columns in constructor order:
        * numeric `c`: `"c"` = (value - mean) / scale, with missing imputed by the mean
          (i.e. 0.0), then `"c__missing"` = 1.0 if missing else 0.0;
        * categorical `c`: `"c=<value>"` for each fitted value in sorted order, then
          `"c=__unknown__"`, which is 1.0 for missing values and values not seen in fit.

    Error contract:
        * `fit` with no rows raises `ValueError`.
        * `transform` before `fit` raises `RuntimeError`.
        * A non-missing numeric value that is not an int/float (booleans excluded) raises
          `ValueError` in `fit` and `transform`.
    """

    feature_names_: list[str]

    def __init__(self, numeric: Sequence[str] = (), categorical: Sequence[str] = ()) -> None:
        """Configure the numeric and categorical column names."""
        raise NotImplementedError("TODO: implement PY-02")

    def fit(self, rows: Sequence[Mapping[str, Any]]) -> "FeatureTransformer":
        """Learn statistics and categories from `rows` and return `self`."""
        raise NotImplementedError("TODO: implement PY-02")

    def transform(self, rows: Sequence[Mapping[str, Any]]) -> list[list[float]]:
        """Encode `rows` with the fitted state; one list of floats per row. Does not refit."""
        raise NotImplementedError("TODO: implement PY-02")

    def fit_transform(self, rows: Sequence[Mapping[str, Any]]) -> list[list[float]]:
        """Equivalent to `fit(rows)` followed by `transform(rows)`."""
        raise NotImplementedError("TODO: implement PY-02")
