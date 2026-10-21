import random

from solution import is_valid_parentheses


def _brute(text):
    while any(pair in text for pair in ("()", "[]", "{}")):
        for pair in ("()", "[]", "{}"):
            text = text.replace(pair, "")
    return text == ""


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "is_valid_parentheses")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_examples():
    assert is_valid_parentheses("()[]{}") is True
    assert is_valid_parentheses("{[]}") is True
    assert is_valid_parentheses("([)]") is False


def test_empty_string_is_valid():
    assert is_valid_parentheses("") is True


def test_single_unmatched_symbols():
    for text in "([{)]}":
        assert is_valid_parentheses(text) is False, text


def test_closer_on_empty_stack():
    assert is_valid_parentheses("())") is False
    assert is_valid_parentheses("]()") is False


def test_leftover_openers():
    assert is_valid_parentheses("(()") is False
    assert is_valid_parentheses("{{[[(())]]}") is False


def test_counts_balance_but_types_mismatch():
    # Per-type counters accept these.
    assert is_valid_parentheses("(]") is False
    assert is_valid_parentheses("([)]{}") is False
    assert is_valid_parentheses("{(})") is False


def test_deep_nesting():
    assert is_valid_parentheses("([{" * 2000 + "}])" * 2000) is True
    assert is_valid_parentheses("([{" * 2000 + "}])" * 1999 + ")]}") is False


def test_matches_reduction_on_random_inputs():
    rng = random.Random(11)
    for _ in range(500):
        text = "".join(rng.choice("()[]{}") for _ in range(rng.randrange(0, 12, 2)))
        assert is_valid_parentheses(text) is _brute(text), text
