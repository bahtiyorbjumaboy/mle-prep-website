def longest_unique_substring(text: str) -> int:
    """Return the longest repeat-free window length in one pass."""
    last_seen: dict[str, int] = {}
    left = 0
    best = 0
    for right, char in enumerate(text):
        # Only jump forward: an older occurrence may sit left of the window already.
        if last_seen.get(char, -1) >= left:
            left = last_seen[char] + 1
        last_seen[char] = right
        best = max(best, right - left + 1)
    return best
