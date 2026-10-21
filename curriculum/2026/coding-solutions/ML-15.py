import numpy as np


class MultinomialNaiveBayes:
    """Multinomial NB with Laplace smoothing; all scoring happens in log space."""

    def __init__(self, alpha: float = 1.0) -> None:
        if alpha <= 0:
            raise ValueError("alpha must be positive")
        self.alpha = alpha

    def fit(self, x: np.ndarray, y: np.ndarray) -> "MultinomialNaiveBayes":
        x = np.asarray(x, dtype=float)
        y = np.asarray(y)
        if x.ndim != 2 or y.shape != (x.shape[0],):
            raise ValueError("expected x (n, d) and y (n,)")
        if np.any(x < 0):
            raise ValueError("counts must be non-negative")
        self.classes_, codes = np.unique(y, return_inverse=True)
        codes = codes.ravel()
        n_classes, d = len(self.classes_), x.shape[1]
        one_hot = np.zeros((len(y), n_classes))
        one_hot[np.arange(len(y)), codes] = 1.0
        feature_counts = one_hot.T @ x  # (C, d): N_cj
        self.class_log_prior_ = np.log(one_hot.sum(axis=0) / len(y))  # documents per class
        smoothed = feature_counts + self.alpha
        self.feature_log_prob_ = np.log(smoothed) - np.log(smoothed.sum(axis=1, keepdims=True))
        return self

    def joint_log_likelihood(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        if x.ndim != 2 or x.shape[1] != self.feature_log_prob_.shape[1]:
            raise ValueError("feature count does not match the fitted model")
        return x @ self.feature_log_prob_.T + self.class_log_prior_

    def predict(self, x: np.ndarray) -> np.ndarray:
        return self.classes_[np.argmax(self.joint_log_likelihood(x), axis=1)]  # first max

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        jll = self.joint_log_likelihood(x)
        shifted = jll - jll.max(axis=1, keepdims=True)  # log-sum-exp shift
        log_norm = np.log(np.exp(shifted).sum(axis=1, keepdims=True))
        return np.exp(shifted - log_norm)
