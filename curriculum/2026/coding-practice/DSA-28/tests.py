import random

from solution import Trie


def _trie(*words):
    trie = Trie()
    for word in words:
        trie.insert(word)
    return trie


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(solution.Trie)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    trie = _trie("app", "apple", "ape")
    assert trie.contains("app") and not trie.contains("ap") and trie.starts_with("ap")
    assert trie.complete("ap", 2) == ["ape", "app"]
    assert trie.complete("ap", 10) == ["ape", "app", "apple"]


def test_empty_trie():
    trie = Trie()
    assert trie.contains("a") is False
    assert trie.starts_with("a") is False
    assert trie.complete("a", 3) == []


def test_word_versus_prefix():
    trie = _trie("apple")
    assert trie.contains("apple") is True
    assert trie.contains("app") is False
    assert trie.starts_with("app") is True
    assert trie.contains("apples") is False
    assert trie.starts_with("apples") is False


def test_word_that_is_prefix_of_another():
    trie = _trie("apple", "app")
    assert trie.contains("app") and trie.contains("apple")
    assert trie.complete("app", 5) == ["app", "apple"]


def test_completion_order_is_lexicographic_not_insertion_order():
    trie = _trie("apz", "apa", "apm")
    assert trie.complete("ap", 2) == ["apa", "apm"]


def test_completion_order_is_lexicographic_not_breadth_first():
    # Breadth-first enumeration returns shorter words first ("ab" before "aab").
    trie = _trie("ab", "aab", "abc")
    assert trie.complete("a", 3) == ["aab", "ab", "abc"]


def test_k_boundaries():
    trie = _trie("a", "ab", "abc")
    assert trie.complete("a", 0) == []
    assert trie.complete("a", 1) == ["a"]
    assert trie.complete("a", 3) == ["a", "ab", "abc"]


def test_missing_prefix_and_duplicate_inserts():
    trie = _trie("cat", "cat", "car")
    assert trie.complete("ca", 5) == ["car", "cat"]
    assert trie.complete("dog", 5) == []


def test_empty_string_word_and_prefix():
    trie = _trie("", "b", "a")
    assert trie.contains("")
    assert trie.starts_with("")
    assert trie.complete("", 5) == ["", "a", "b"]


def test_unicode_words():
    trie = _trie("über", "ubiquitous", "übel")
    assert trie.contains("über") and not trie.contains("ube")
    assert trie.complete("üb", 5) == ["übel", "über"]


def test_matches_sorted_filter_on_random_words():
    rng = random.Random(28)
    words = {"".join(rng.choice("abc") for _ in range(rng.randint(1, 5))) for _ in range(150)}
    trie = Trie()
    for word in sorted(words, key=lambda _: rng.random()):
        trie.insert(word)
    for _ in range(200):
        prefix = "".join(rng.choice("abc") for _ in range(rng.randint(0, 3)))
        k = rng.randint(0, 8)
        matches = sorted(w for w in words if w.startswith(prefix))
        assert trie.complete(prefix, k) == matches[:k], (prefix, k)
        assert trie.starts_with(prefix) == bool(matches)
        assert trie.contains(prefix) == (prefix in words)
