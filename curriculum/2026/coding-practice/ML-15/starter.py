import numpy as np


class MultinomialNaiveBayes:
    """Multinomial Naive Bayes for count features.

    Canonical prompt: implement multinomial Naive Bayes for count features with
    Laplace smoothing and log-space prediction. Return class log-priors, feature
    log-probabilities, predicted classes, and optional normalized probabilities.

    Contract (`alpha > 0`, ValueError otherwise):
    - `fit(x, y)`: `x` `(n, d)` non-negative counts, `y` `(n,)` labels (ints or strings).
      `classes_` = sorted unique labels.
      `class_log_prior_[c] = log(n_docs_c / n)` (document counts, not token counts).
      `feature_log_prob_[c, j] = log((N_cj + alpha) / (N_c + alpha * d))` where `N_cj` is
      the total count of feature j in class c and `N_c = sum_j N_cj`.
    - `joint_log_likelihood(x) = x @ feature_log_prob_.T + class_log_prior_`, shape `(q, C)`.
      Stay in log space: never multiply raw probabilities (long documents underflow).
    - `predict(x)`: label with the largest joint log-likelihood; ties -> smallest label.
    - `predict_proba(x)`: `(q, C)` rows normalized with a stable log-sum-exp; finite
      and summing to 1 even when every joint log-likelihood is around -1e5.

    Raises:
        ValueError: negative counts, shape mismatches, `alpha <= 0`, or a feature-count
            mismatch at prediction time.
    """

    def __init__(self, alpha: float = 1.0) -> None:
        raise NotImplementedError("TODO: implement ML-15")

    def fit(self, x: np.ndarray, y: np.ndarray) -> "MultinomialNaiveBayes":
        raise NotImplementedError("TODO: implement ML-15")

    def joint_log_likelihood(self, x: np.ndarray) -> np.ndarray:
        raise NotImplementedError("TODO: implement ML-15")

    def predict(self, x: np.ndarray) -> np.ndarray:
        raise NotImplementedError("TODO: implement ML-15")

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        raise NotImplementedError("TODO: implement ML-15")
