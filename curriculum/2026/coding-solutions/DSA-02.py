from collections import Counter, defaultdict


def group_anagrams(words: list[str]) -> list[list[str]]:
    """Group words by their character multiset."""
    groups: defaultdict[frozenset, list[str]] = defaultdict(list)
    for word in words:
        # A frozen Counter key is O(len(word)) and works for any alphabet.
        groups[frozenset(Counter(word).items())].append(word)
    return list(groups.values())
