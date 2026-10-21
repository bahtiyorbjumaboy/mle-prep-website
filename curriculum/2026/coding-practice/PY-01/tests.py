import json
import random

from solution import process_events

CATEGORIES = "item_id,category\n10,books\n11,games\n12,books\n13,music\n"


def _line(**fields):
    return json.dumps(fields)


def _run(*args, **kwargs):
    """Call process_events and normalize pair/triple containers to tuples."""
    out = dict(process_events(*args, **kwargs))
    out["sessions"] = {user: [tuple(s) for s in sessions] for user, sessions in out["sessions"].items()}
    out["top_categories"] = [tuple(pair) for pair in out["top_categories"]]
    return out


def test_implementation_replaces_todo():
    import inspect
    import solution
    source = inspect.getsource(solution.process_events)
    assert "NotImplementedError" not in source and "TODO: implement" not in source


def test_hand_computed_summary():
    lines = [
        _line(user_id=2, event="click", item_id=11, ts=100),
        _line(user_id=1, event="click", item_id=10, ts=50),
        "not json",
        _line(user_id=1, event="purchase", item_id=10, ts=4000, amount=20.5),
        _line(user_id=1, event="click", item_id=12, ts=60),
        _line(user_id=2, event="purchase", item_id=11, ts=200, amount=7),
        _line(user_id=2, event="view", ts=2100),
    ]
    out = _run(lines, CATEGORIES)
    assert out["malformed_count"] == 1
    assert out["highest_spender"] == 1
    assert out["top_categories"] == [("books", 2), ("games", 1)]
    assert out["sessions"] == {
        1: [(50, 60, 2), (4000, 4000, 1)],
        2: [(100, 200, 2), (2100, 2100, 1)],
    }


def test_empty_input():
    out = _run([], CATEGORIES)
    assert out == {"sessions": {}, "top_categories": [], "highest_spender": None, "malformed_count": 0}


def test_malformed_lines_are_counted_not_raised():
    lines = [
        "{bad json",
        "[1, 2, 3]",
        "null",
        _line(event="click", item_id=10, ts=1),  # missing user_id
        _line(user_id=1, event="click", ts=1),  # click without item_id
        _line(user_id=1, event="purchase", item_id=10, ts=1),  # purchase without amount
        _line(user_id=1, event="purchase", item_id=10, ts=1, amount=-5),
        _line(user_id=1, event="purchase", item_id=10, ts=1, amount="9"),
        _line(user_id=1, event="click", item_id=10, ts="yesterday"),
        _line(user_id=True, event="click", item_id=10, ts=1),
        _line(user_id=1, event="click", item_id=10, ts=True),
        _line(user_id="1", event="click", item_id=10, ts=1),
        _line(user_id=1, event="click", item_id=10, ts=5),
    ]
    out = _run(lines, CATEGORIES)
    assert out["malformed_count"] == 12
    assert out["sessions"] == {1: [(5, 5, 1)]}


def test_blank_lines_are_ignored():
    lines = ["", "   ", "\n", _line(user_id=1, event="click", item_id=10, ts=1) + "\n"]
    out = _run(lines, CATEGORIES)
    assert out["malformed_count"] == 0 and out["sessions"] == {1: [(1, 1, 1)]}


def test_session_gap_boundary_is_inclusive():
    lines = [_line(user_id=7, event="view", ts=t) for t in (0, 30, 60, 91)]
    out = _run(lines, CATEGORIES, session_gap=30)
    assert out["sessions"] == {7: [(0, 60, 3), (91, 91, 1)]}


def test_sessions_sort_unsorted_events():
    times = [500, 0, 100, 3000, 200]
    out = _run([_line(user_id=3, event="view", ts=t) for t in times], CATEGORIES, session_gap=1800)
    assert out["sessions"] == {3: [(0, 500, 4), (3000, 3000, 1)]}


def test_item_ids_match_by_string_and_unknown_items():
    lines = [
        _line(user_id=1, event="click", item_id=13, ts=1),
        _line(user_id=1, event="click", item_id="13", ts=2),
        _line(user_id=1, event="click", item_id=999, ts=3),
    ]
    out = _run(lines, CATEGORIES)
    assert out["top_categories"] == [("music", 2), ("unknown", 1)]


def test_csv_is_parsed_as_csv():
    csv_text = 'category,item_id\n"Books, Used",10\nmusic,11\n'
    lines = [_line(user_id=1, event="click", item_id=10, ts=1), _line(user_id=1, event="click", item_id=11, ts=2)]
    out = _run(lines, csv_text)
    assert out["top_categories"] == [("Books, Used", 1), ("music", 1)]


def test_top_categories_ties_and_k():
    clicks = {10: 2, 11: 3, 13: 2}  # books=2, games=3, music=2
    lines = [_line(user_id=1, event="click", item_id=i, ts=n) for i, c in clicks.items() for n in range(c)]
    lines.append(_line(user_id=1, event="purchase", item_id=13, ts=9, amount=1))  # purchases are not clicks
    assert _run(lines, CATEGORIES, top_k=2)["top_categories"] == [("games", 3), ("books", 2)]
    assert _run(lines, CATEGORIES, top_k=10)["top_categories"] == [("games", 3), ("books", 2), ("music", 2)]


def test_highest_spender_sums_purchases_and_breaks_ties():
    lines = [
        _line(user_id=5, event="purchase", item_id=10, ts=1, amount=10),
        _line(user_id=3, event="purchase", item_id=10, ts=2, amount=4),
        _line(user_id=3, event="purchase", item_id=11, ts=3, amount=6.0),
        _line(user_id=9, event="purchase", item_id=11, ts=4, amount=9.5),
    ]
    assert _run(lines, CATEGORIES)["highest_spender"] == 3
    clicks_only = [_line(user_id=1, event="click", item_id=10, ts=1)]
    assert _run(clicks_only, CATEGORIES)["highest_spender"] is None


def test_accepts_one_shot_iterator():
    def stream():
        yield _line(user_id=1, event="click", item_id=10, ts=1)
        yield "oops"
        yield _line(user_id=1, event="purchase", item_id=10, ts=2, amount=3)

    out = _run(stream(), CATEGORIES)
    assert out["malformed_count"] == 1
    assert out["sessions"] == {1: [(1, 2, 2)]} and out["highest_spender"] == 1


def test_result_is_independent_of_event_order():
    rng = random.Random(101)
    lines = [
        _line(user_id=rng.randint(1, 4), event=rng.choice(["click", "purchase", "view"]),
              item_id=rng.choice([10, 11, 12, 13, 99]), ts=rng.randint(0, 10_000), amount=rng.randint(0, 50))
        for _ in range(200)
    ] + ["garbage"] * 3
    expected = _run(list(lines), CATEGORIES, session_gap=600)
    for _ in range(3):
        rng.shuffle(lines)
        assert _run(list(lines), CATEGORIES, session_gap=600) == expected


def test_uses_only_the_standard_library():
    import inspect
    import solution
    source = inspect.getsource(solution)
    for banned in ("pandas", "numpy", "polars"):
        assert f"import {banned}" not in source and f"from {banned}" not in source, banned
