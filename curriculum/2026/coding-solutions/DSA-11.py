def is_valid_parentheses(text: str) -> bool:
    """Return whether brackets in text are properly matched and nested."""
    closer_to_opener = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for char in text:
        if char in closer_to_opener:
            if not stack or stack.pop() != closer_to_opener[char]:
                return False
        else:
            stack.append(char)
    return not stack
