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


def _delta(change: str) -> str:
    """The stat card's change line: "▲ 0.17 from last week" (empty without a change)."""
    if not change:
        return ""
    v = float(change)
    if v == 0:
        return "unchanged from last week"
    return f"{'▲' if v > 0 else '▼'} {change.lstrip('+-')} from last week"


def _delta_short(change: str) -> str:
    """The change for the short version: "▲0.17", "▼0.07", "unchanged" ("" without one)."""
    if not change:
        return ""
    v = float(change)
    return "unchanged" if v == 0 else f"{'▲' if v > 0 else '▼'}{change.lstrip('+-')}"


def _nmls_tail(profile: dict) -> str:
    """The company's NMLS on the card's context line: the name slot under the
    card is too narrow for "Company LLC, NMLS #..." (cut on the 2026-11-24
    render), so the name goes there and the number here."""
    nmls = str(profile.get("company_nmls_id", "")).strip()
    return f" Company NMLS #{nmls}." if nmls else ""


def _context(week: dict) -> str:
    parts = []
    if week.get("rate_15"):
        parts.append(f"15-year: {week['rate_15']}%")
    if week.get("year_ago_rate_30"):
        parts.append(f"30-year a year ago: {week['year_ago_rate_30']}%")
    return ". ".join(parts) + ("." if parts else "")


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
              "direction_15": _direction(week["change_15"]),
              # short version for X, Bluesky, Threads: the rate and the change
              "delta_short": _delta_short(week.get("change_30", "")),
              "delta_paren": f" ({_delta_short(week['change_30'])})" if week.get("change_30") else "",
              # the size of the change, as both versions write it ("up 0.17 points", "▲0.17")
              "change_abs": (week.get("change_30") or "").lstrip("+-") if week.get("change_30")
              and float(week["change_30"]) != 0 else ""}
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
                 "delta": _delta(week.get("change_30", "")),
                 "context": _context(week) + _nmls_tail(config.get("profile") or {}),
                 # The card travels without its post (reshares, screenshots), so it
                 # carries the not-an-offer line and the company's NMLS itself.
                 "source": "PMMS weekly national average, not an offer of credit",
                 **({"name": str((config.get("profile") or {}).get("company_name", "")).strip()}
                    if (config.get("profile") or {}).get("company_name") else {})},
    }]
