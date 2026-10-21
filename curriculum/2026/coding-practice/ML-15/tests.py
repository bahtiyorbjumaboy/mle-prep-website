import math

import numpy as np

from solution import MultinomialNaiveBayes


def _raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


X = np.array([[2, 1, 0], [1, 0, 0], [0, 0, 3], [0, 1, 2], [3, 0, 0]])
Y = np.array([0, 0, 1, 1, 0])


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(getattr(solution, "MultinomialNaiveBayes"))
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_priors_use_document_counts():
    model = MultinomialNaiveBayes().fit(X, Y)
    assert model.classes_.tolist() == [0, 1]
    assert np.allclose(model.class_log_prior_, np.log([3 / 5, 2 / 5]))
    heavy = MultinomialNaiveBayes().fit(np.array([[100, 0], [0, 1], [0, 1]]), np.array([0, 1, 1]))
    assert np.allclose(heavy.class_log_prior_, np.log([1 / 3, 2 / 3]))


def test_laplace_smoothed_feature_log_probs_hand_computed():
    model = MultinomialNaiveBayes(alpha=1.0).fit(X, Y)
    # class 0 counts [6, 1, 0] (N=7); class 1 counts [0, 1, 5] (N=6); d=3
    expected = np.log([[7 / 10, 2 / 10, 1 / 10], [1 / 9, 2 / 9, 6 / 9]])
    assert model.feature_log_prob_.shape == (2, 3)
    assert np.allclose(model.feature_log_prob_, expected)
    half = MultinomialNaiveBayes(alpha=0.5).fit(X, Y)
    assert np.allclose(half.feature_log_prob_[0], np.log(np.array([6.5, 1.5, 0.5]) / 8.5))
    assert np.allclose(np.exp(model.feature_log_prob_).sum(axis=1), 1.0)


def test_unseen_tokens_stay_finite():
    model = MultinomialNaiveBayes().fit(X, Y)
    assert np.all(np.isfinite(model.feature_log_prob_))
    jll = model.joint_log_likelihood(np.array([[0, 0, 7]]))  # feature 2 never seen in class 0
    assert np.all(np.isfinite(jll)) and model.predict(np.array([[0, 0, 7]])).tolist() == [1]


def test_joint_log_likelihood_and_prediction():
    model = MultinomialNaiveBayes().fit(X, Y)
    q = np.array([[1, 1, 1], [4, 0, 1], [0, 2, 0]])
    expected = q @ model.feature_log_prob_.T + model.class_log_prior_
    assert np.allclose(model.joint_log_likelihood(q), expected)
    assert model.predict(q).tolist() == np.argmax(expected, axis=1).tolist()


def test_long_documents_do_not_underflow():
    rng = np.random.default_rng(0)
    probs = np.array([[0.7, 0.2, 0.1], [0.2, 0.3, 0.5]])
    y = np.repeat([0, 1], 50)
    x = np.vstack([rng.multinomial(200, probs[c]) for c in y])
    model = MultinomialNaiveBayes().fit(x, y)
    long_docs = np.array([[70000, 20000, 10000], [20000, 30000, 50000]])
    jll = model.joint_log_likelihood(long_docs)
    assert np.all(jll < -5e4)  # raw probabilities would be exactly 0.0 in float64
    proba = model.predict_proba(long_docs)
    assert np.all(np.isfinite(proba)) and np.allclose(proba.sum(axis=1), 1.0)
    assert model.predict(long_docs).tolist() == [0, 1]
    assert proba[0, 0] > 0.99 and proba[1, 1] > 0.99


def test_predict_proba_matches_softmax_of_joint_log_likelihood():
    model = MultinomialNaiveBayes().fit(X, Y)
    q = np.array([[1, 0, 1], [0, 0, 0]])
    jll = model.joint_log_likelihood(q)
    expected = np.exp(jll - jll.max(axis=1, keepdims=True))
    expected /= expected.sum(axis=1, keepdims=True)
    assert np.allclose(model.predict_proba(q), expected)


def test_empty_document_predicts_prior_and_multiclass_strings():
    labels = np.array(["sport", "tech", "sport", "food", "tech", "tech"])
    x = np.array([[3, 0, 0, 1], [0, 2, 1, 0], [2, 1, 0, 0], [0, 0, 0, 4], [0, 3, 0, 0], [1, 2, 2, 0]])
    model = MultinomialNaiveBayes().fit(x, labels)
    assert model.classes_.tolist() == ["food", "sport", "tech"]
    assert model.predict(np.zeros((1, 4), dtype=int)).tolist() == ["tech"]
    assert np.allclose(model.predict_proba(np.zeros((1, 4))), [[1 / 6, 2 / 6, 3 / 6]])
    assert model.predict(np.array([[0, 0, 0, 3], [4, 0, 0, 0]])).tolist() == ["food", "sport"]


def test_ties_go_to_smallest_label_and_never_seen_feature_column():
    model = MultinomialNaiveBayes().fit(np.array([[1, 0, 0], [0, 1, 0]]), np.array(["b", "a"]))
    assert model.predict(np.array([[1, 1, 0], [0, 0, 5]])).tolist() == ["a", "a"]
    assert math.isclose(model.feature_log_prob_[0, 2], math.log(1 / 4))


def test_validation():
    assert _raises(ValueError, MultinomialNaiveBayes, 0.0)
    assert _raises(ValueError, MultinomialNaiveBayes().fit, np.array([[1, -1]]), np.array([0]))
    assert _raises(ValueError, MultinomialNaiveBayes().fit, X, Y[:3])
    model = MultinomialNaiveBayes().fit(X, Y)
    assert _raises(ValueError, model.predict, np.ones((1, 4)))
