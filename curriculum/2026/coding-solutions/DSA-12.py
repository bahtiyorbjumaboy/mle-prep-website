def daily_temperatures(temperatures: list[int]) -> list[int]:
    """Return days until a warmer temperature using a monotonic stack of indices."""
    answer = [0] * len(temperatures)
    stack: list[int] = []  # indices of days still waiting, temperatures non-increasing
    for day, temp in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temp:
            previous = stack.pop()
            answer[previous] = day - previous
        stack.append(day)
    return answer
