class _Node:
    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        self.children: dict[str, "_Node"] = {}
        self.is_word = False


class Trie:
    """Prefix tree with exact lookup, prefix lookup, and ordered completions."""

    def __init__(self) -> None:
        self.root = _Node()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            node = node.children.setdefault(char, _Node())
        node.is_word = True

    def _find(self, prefix: str) -> "_Node | None":
        node = self.root
        for char in prefix:
            node = node.children.get(char)
            if node is None:
                return None
        return node

    def contains(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        node = self._find(prefix)
        # Nodes are only created by insert, so any reachable node has a word beneath it.
        return node is not None and (node.is_word or bool(node.children))

    def complete(self, prefix: str, k: int) -> list[str]:
        start = self._find(prefix)
        results: list[str] = []
        if start is None or k <= 0:
            return results
        # Pre-order DFS with sorted children yields words in lexicographic order,
        # so enumeration can stop as soon as k words are found.
        stack = [(start, prefix)]
        while stack and len(results) < k:
            node, text = stack.pop()
            if node.is_word:
                results.append(text)
            for char in sorted(node.children, reverse=True):
                stack.append((node.children[char], text + char))
        return results
