class Trie:
    """Prefix index over strings.

    `insert`, `contains`, and `starts_with` run in O(length of the argument).
    `complete` is output-sensitive: it should not visit every word under the prefix when
    only `k` are requested.
    """

    def __init__(self) -> None:
        """Create an empty trie."""
        raise NotImplementedError("TODO: implement DSA-28")

    def insert(self, word: str) -> None:
        """Add `word`; inserting the same word again has no further effect."""
        raise NotImplementedError("TODO: implement DSA-28")

    def contains(self, word: str) -> bool:
        """Return whether `word` itself was inserted (a mere prefix does not count)."""
        raise NotImplementedError("TODO: implement DSA-28")

    def starts_with(self, prefix: str) -> bool:
        """Return whether at least one inserted word starts with `prefix`."""
        raise NotImplementedError("TODO: implement DSA-28")

    def complete(self, prefix: str, k: int) -> list[str]:
        """Return up to `k` inserted words that start with `prefix`, in lexicographic order.

        The prefix itself is included when it is an inserted word. Returns `[]` when
        `k <= 0` or no word matches.
        """
        raise NotImplementedError("TODO: implement DSA-28")
