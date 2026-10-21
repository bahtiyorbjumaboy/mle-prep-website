import csv
import io
import json
from collections import Counter, defaultdict
from typing import Any, Iterable, Iterator


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _parse(line: str) -> dict[str, Any] | None:
    """Return a validated event dict, or None if the line is malformed."""
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(event, dict):
        return None
    user_id, kind, ts = event.get("user_id"), event.get("event"), event.get("ts")
    if not (isinstance(user_id, int) and not isinstance(user_id, bool)):
        return None
    if not isinstance(kind, str) or not _is_number(ts):
        return None
    if kind in ("click", "purchase") and not isinstance(event.get("item_id"), (int, str)):
        return None
    if kind == "purchase" and not (_is_number(event.get("amount")) and event["amount"] >= 0):
        return None
    return event


def iter_events(json_lines: Iterable[str], malformed: Counter) -> Iterator[dict[str, Any]]:
    """Lazily yield valid events; count malformed lines in `malformed["count"]`."""
    for line in json_lines:
        if not line.strip():
            continue
        event = _parse(line)
        if event is None:
            malformed["count"] += 1
        else:
            yield event


def process_events(
    json_lines: Iterable[str],
    category_csv: str,
    session_gap: float = 1800,
    top_k: int = 3,
) -> dict[str, Any]:
    """Summarize events: sessions, top clicked categories, highest spender, malformed count."""
    category_of = {row["item_id"]: row["category"] for row in csv.DictReader(io.StringIO(category_csv))}

    malformed: Counter = Counter()
    clicks: Counter = Counter()
    spend: defaultdict[int, float] = defaultdict(float)
    times: defaultdict[int, list[float]] = defaultdict(list)
    # Counts and totals stream; sessions need each user's timestamps buffered and sorted.
    for event in iter_events(json_lines, malformed):
        user = event["user_id"]
        times[user].append(event["ts"])
        if event["event"] == "click":
            clicks[category_of.get(str(event["item_id"]), "unknown")] += 1
        elif event["event"] == "purchase":
            spend[user] += event["amount"]

    sessions: dict[int, list[tuple[float, float, int]]] = {}
    for user, stamps in times.items():
        stamps.sort()
        user_sessions = []
        start = previous = stamps[0]
        count = 0
        for ts in stamps:
            if ts - previous > session_gap:
                user_sessions.append((start, previous, count))
                start, count = ts, 0
            previous = ts
            count += 1
        user_sessions.append((start, previous, count))
        sessions[user] = user_sessions

    top = sorted(clicks.items(), key=lambda kv: (-kv[1], kv[0]))[:top_k]
    spender = min(spend, key=lambda u: (-spend[u], u)) if spend else None
    return {
        "sessions": sessions,
        "top_categories": top,
        "highest_spender": spender,
        "malformed_count": malformed["count"],
    }
