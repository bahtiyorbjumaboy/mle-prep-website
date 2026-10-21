import math
from typing import Any, Mapping, Sequence

UNKNOWN = "__unknown__"


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def _numeric(column: str, value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"column {column!r} expects a number, got {value!r}")
    return float(value)


class FeatureTransformer:
    """Standardize/impute/flag numeric columns and one-hot encode categorical columns."""

    def __init__(self, numeric: Sequence[str] = (), categorical: Sequence[str] = ()) -> None:
        self.numeric = list(numeric)
        self.categorical = list(categorical)
        self._fitted = False

    def fit(self, rows: Sequence[Mapping[str, Any]]) -> "FeatureTransformer":
        if not rows:
            raise ValueError("fit requires at least one row")
        # Build all new state locally, then swap it in, so a failed fit keeps no partial state.
        stats: dict[str, tuple[float, float]] = {}
        for column in self.numeric:
            values = [_numeric(column, row.get(column)) for row in rows if not _is_missing(row.get(column))]
            mean = sum(values) / len(values) if values else 0.0
            std = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values)) if values else 0.0
            stats[column] = (mean, std if std > 0 else 1.0)
        categories = {
            column: sorted({row.get(column) for row in rows if not _is_missing(row.get(column))})
            for column in self.categorical
        }
        names = [name for column in self.numeric for name in (column, f"{column}__missing")]
        for column in self.categorical:
            names += [f"{column}={value}" for value in categories[column]] + [f"{column}={UNKNOWN}"]

        self.stats_, self.categories_, self.feature_names_ = stats, categories, names
        self._index = {column: {v: i for i, v in enumerate(categories[column])} for column in self.categorical}
        self._fitted = True
        return self

    def transform(self, rows: Sequence[Mapping[str, Any]]) -> list[list[float]]:
        if not self._fitted:
            raise RuntimeError("FeatureTransformer must be fit before transform")
        out = []
        for row in rows:
            features: list[float] = []
            for column in self.numeric:
                mean, scale = self.stats_[column]
                value = row.get(column)
                if _is_missing(value):
                    features += [0.0, 1.0]
                else:
                    features += [(_numeric(column, value) - mean) / scale, 0.0]
            for column in self.categorical:
                index = self._index[column]
                one_hot = [0.0] * (len(index) + 1)
                value = row.get(column)
                position = index.get(value, len(index)) if not _is_missing(value) else len(index)
                one_hot[position] = 1.0
                features += one_hot
            out.append(features)
        return out

    def fit_transform(self, rows: Sequence[Mapping[str, Any]]) -> list[list[float]]:
        return self.fit(rows).transform(rows)
