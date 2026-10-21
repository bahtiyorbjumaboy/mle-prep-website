class UnionFind:
    """Disjoint-set union over elements `0..n-1` with path compression and union by rank/size.

    Attributes:
        parent: `parent[i]` is the parent of `i` in the forest; roots satisfy `parent[i] == i`.
            `find` must compress the path it walks so visited nodes point directly at the root.
        count: Current number of disjoint sets (connected components).
    """

    def __init__(self, n: int) -> None:
        """Create `n` singleton sets."""
        raise NotImplementedError("TODO: implement DSA-29")

    def find(self, x: int) -> int:
        """Return the representative (root) of the set containing `x`."""
        raise NotImplementedError("TODO: implement DSA-29")

    def union(self, a: int, b: int) -> bool:
        """Merge the sets containing `a` and `b`.

        Returns:
            `True` if two different sets were merged, `False` if they were already joined.
        """
        raise NotImplementedError("TODO: implement DSA-29")

    def connected(self, a: int, b: int) -> bool:
        """Return whether `a` and `b` are in the same set."""
        raise NotImplementedError("TODO: implement DSA-29")
