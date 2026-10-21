import random

from solution import longest_unique_substring


def _brute(text):
    best = 0
    for i in range(len(text)):
        for j in range(i, len(text)):
            if len(set(text[i:j + 1])) == j - i + 1:
                best = max(best, j - i + 1)
    return best


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "longest_unique_substring")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    assert longest_unique_substring("abcabcbb") == 3


def test_empty_and_singleton():
    assert longest_unique_substring("") == 0
    assert longest_unique_substring("a") == 1


def test_all_repeated():
    assert longest_unique_substring("bbbbb") == 1


def test_substring_not_subsequence():
    # "pwke" is a subsequence, not a substring.
    assert longest_unique_substring("pwwkew") == 3


def test_last_seen_index_must_not_move_window_backwards():
    # Jumping left to last_seen + 1 without max() re-admits the earlier "a".
    assert longest_unique_substring("abba") == 2
    assert longest_unique_substring("tmmzuxt") == 5


def test_window_must_not_reset_on_repeat():
    # Clearing the whole window on a repeat loses "vdf".
    assert longest_unique_substring("dvdf") == 3


def test_entire_string_unique_and_spaces():
    assert longest_unique_substring("abcdef") == 6
    assert longest_unique_substring("a a") == 2
    assert longest_unique_substring("日本日本語") == 3


def test_matches_brute_force_on_random_inputs():
    rng = random.Random(7)
    for _ in range(300):
        text = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 16)))
        assert longest_unique_substring(text) == _brute(text), text
