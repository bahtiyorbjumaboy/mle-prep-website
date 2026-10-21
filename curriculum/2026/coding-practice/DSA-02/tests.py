import random

from solution import group_anagrams


def _normalize(groups):
    return sorted(sorted(group) for group in groups)


def test_implementation_replaces_todo():
    import inspect
    import solution
    target = getattr(solution, "group_anagrams")
    source = inspect.getsource(target)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_example():
    result = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert _normalize(result) == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]


def test_empty_input_and_empty_strings():
    assert group_anagrams([]) == []
    assert _normalize(group_anagrams(["", ""])) == [["", ""]]
    assert _normalize(group_anagrams(["", "a"])) == [[""], ["a"]]


def test_repeated_words_are_kept():
    assert _normalize(group_anagrams(["ab", "ab", "ba"])) == [["ab", "ab", "ba"]]


def test_multiplicity_matters_not_just_presence():
    # A set-of-characters key would merge these.
    assert _normalize(group_anagrams(["aab", "abb", "ab"])) == [["aab"], ["ab"], ["abb"]]


def test_count_key_is_unambiguous():
    # Concatenating counts without a separator maps a*11+b and a+b*11 to the same key.
    first, second = "a" * 11 + "b", "a" + "b" * 11
    assert _normalize(group_anagrams([first, second])) == [[first], [second]]


def test_case_sensitive_unicode_strings():
    result = group_anagrams(["Ab", "bA", "ab", "éa", "aé", "ß"])
    assert _normalize(result) == [["Ab", "bA"], ["ab"], ["aé", "éa"], ["ß"]]


def test_matches_reference_grouping_on_random_inputs():
    rng = random.Random(2)
    for _ in range(100):
        words = ["".join(rng.choice("abc") for _ in range(rng.randint(0, 4))) for _ in range(rng.randint(0, 15))]
        expected = {}
        for word in words:
            expected.setdefault("".join(sorted(word)), []).append(word)
        result = group_anagrams(list(words))
        assert sorted(word for group in result for word in group) == sorted(words), "every word must appear exactly once"
        assert _normalize(result) == _normalize(expected.values()), words
