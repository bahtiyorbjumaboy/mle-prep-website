from typing import Any, Iterable


def process_events(
    json_lines: Iterable[str],
    category_csv: str,
    session_gap: float = 1800,
    top_k: int = 3,
) -> dict[str, Any]:
    """Summarize unsorted JSONL events joined to an item-category CSV (standard library only).

    Event lines are JSON objects. A line is valid when it has:
        * `user_id`: int; `event`: str; `ts`: int or float (booleans are not numbers);
        * for `event` in {"click", "purchase"}: `item_id` (int or str);
        * for `event == "purchase"`: `amount`, an int or float >= 0.
    Any other non-blank line (bad JSON, non-object JSON, missing/ill-typed fields) is
    malformed. Blank or whitespace-only lines are ignored and not counted.

    `category_csv` is CSV text with a header containing `item_id` and `category` columns
    (in any order; fields may be quoted). Item ids are matched by their string form, so
    JSON `10` matches CSV `"10"`. Clicked items missing from the CSV count as "unknown".

    `json_lines` may be a one-shot iterator (e.g. an open file); read it only once.

    Args:
        json_lines: Event lines (in any timestamp order).
        category_csv: Item-to-category CSV text.
        session_gap: A user's next event starts a new session when it is more than
            `session_gap` seconds after the previous event; exactly `session_gap` apart
            stays in the same session.
        top_k: Number of categories to report.

    Returns:
        A dict with keys:
            "sessions": {user_id: [(start_ts, end_ts, event_count), ...]} for every user
                with a valid event, sessions in time order (all event types count).
            "top_categories": up to `top_k` `(category, click_count)` pairs ordered by
                count descending, then category ascending.
            "highest_spender": user_id with the largest total purchase amount (ties go to
                the smallest user_id), or None if there are no valid purchases.
            "malformed_count": number of malformed lines.
    """
    raise NotImplementedError("TODO: implement PY-01")
