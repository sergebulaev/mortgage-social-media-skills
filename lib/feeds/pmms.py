"""Freddie Mac Primary Mortgage Market Survey (weekly, Thursdays 12:00 ET).

Full-history CSV, free, no key. Columns: date (M/D/YYYY), pmms30, pmms30p
(points), pmms15, pmms15p, pmms51... Blank cells are empty strings.
`latest()` returns this week, last week, the change and the year-ago week,
all as the strings the CSV holds, so a post can quote them exactly.
"""
from __future__ import annotations

import csv
import datetime as dt
import io

from .. import _http

URL = "https://www.freddiemac.com/pmms/docs/PMMS_history.csv"
FIXTURE = "pmms-history-tail.csv"
SOURCE = "Freddie Mac Primary Mortgage Market Survey"
SOURCE_URL = "https://www.freddiemac.com/pmms"


def fetch() -> bytes:
    return _http.get_bytes(URL, timeout=60)


def parse(raw: bytes) -> list[dict]:
    rows = []
    for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        try:
            d = dt.datetime.strptime(r["date"].strip(), "%m/%d/%Y").date()
        except (KeyError, ValueError):
            continue
        rows.append({"date": d.isoformat(), "rate_30": (r.get("pmms30") or "").strip(),
                     "rate_15": (r.get("pmms15") or "").strip()})
    return rows


def _diff(a: str, b: str) -> str:
    if not a or not b:
        return ""
    return f"{float(a) - float(b):+.2f}"


def latest(rows: list[dict]) -> dict:
    """This week vs last week vs the same week a year ago."""
    rows = [r for r in rows if r["rate_30"]]
    cur, prev = rows[-1], rows[-2]
    d = dt.date.fromisoformat(cur["date"])
    year_ago = min(rows, key=lambda r: abs((dt.date.fromisoformat(r["date"]) - (d - dt.timedelta(days=364))).days))
    return {
        "source": SOURCE, "source_url": SOURCE_URL, "week_of": cur["date"],
        "rate_30": cur["rate_30"], "rate_15": cur["rate_15"],
        "prev_week": prev["date"], "prev_rate_30": prev["rate_30"], "prev_rate_15": prev["rate_15"],
        "change_30": _diff(cur["rate_30"], prev["rate_30"]),
        "change_15": _diff(cur["rate_15"], prev["rate_15"]),
        "year_ago_week": year_ago["date"], "year_ago_rate_30": year_ago["rate_30"],
        "year_ago_rate_15": year_ago["rate_15"],
        "change_30_yoy": _diff(cur["rate_30"], year_ago["rate_30"]),
    }


def check(rows: list[dict]) -> list[str]:
    problems = []
    if len(rows) < 2:
        problems.append("fewer than 2 rows")
    elif not rows[-1]["rate_30"]:
        problems.append("latest row has no 30-year rate (column renamed?)")
    else:
        age = (dt.date.today() - dt.date.fromisoformat(rows[-1]["date"])).days
        if age > 15:
            problems.append(f"latest week is {age} days old")
    return problems
