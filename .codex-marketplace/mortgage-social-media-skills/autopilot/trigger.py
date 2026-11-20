"""Autopilot trigger: a new Freddie Mac PMMS week -> one rate post event.

Contract (autopilot/watch.py): events(config, fixtures, today) -> list of
{"id", "title", "template", "fields", "data", "angle", "card"}.
The event id is the survey week, so a week is drafted once however often the
workflow runs (Thursday and Friday).
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.feeds import pmms  # noqa: E402

MAX_AGE_DAYS = 6  # a survey older than this is last week's: no event


def _pretty(iso: str) -> str:
    d = dt.date.fromisoformat(iso)
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def _direction(change: str) -> str:
    if not change:
        return "compared with"
    v = float(change)
    if v > 0:
        return f"up {change.lstrip('+')} points from"
    if v < 0:
        return f"down {change.lstrip('-')} points from"
    return "unchanged from"


def events(config: dict, fixtures: Path | None = None, today: str = "") -> list[dict]:
    raw = (Path(fixtures) / pmms.FIXTURE).read_bytes() if fixtures else pmms.fetch()
    rows = pmms.parse(raw)
    problems = pmms.check(rows) if not fixtures else []
    if problems:
        raise RuntimeError("PMMS feed: " + "; ".join(problems))
    week = pmms.latest(rows)
    today_d = dt.date.fromisoformat(today) if today else dt.date.today()
    if (today_d - dt.date.fromisoformat(week["week_of"])).days > MAX_AGE_DAYS:
        return []
    data = {**week, "term_30": "30-year", "term_15": "15-year",
            "week_label": _pretty(week["week_of"]), "prev_label": _pretty(week["prev_week"]),
            "year_ago_label": _pretty(week["year_ago_week"])}
    fields = {**data, "direction_30": _direction(week["change_30"]),
              "direction_15": _direction(week["change_15"])}
    return [{
        "id": f"pmms-{week['week_of']}",
        "title": f"Freddie Mac PMMS, week of {data['week_label']}",
        "template": "rate_week",
        "fields": fields,
        "data": data,
        "angle": ("This week's Freddie Mac PMMS averages vs last week and a year ago, explained for "
                  "someone shopping for a home loan. Market news, not an offer: no payment amounts, "
                  "no down payment percentages, no 'my rate', no forecast."),
        "card": {"kind": "stat", "value": f"{week['rate_30']}%",
                 "label": f"30-year fixed, Freddie Mac PMMS average, week of {data['week_label']}",
                 "source": "Freddie Mac PMMS"},
    }]
