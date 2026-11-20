"""US public holidays (date.nager.at, free JSON, no key)."""
from __future__ import annotations

import json

from .. import _http

URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/US"
FIXTURE = "holidays-2026-us.json"


def fetch(year: int) -> bytes:
    return _http.get_bytes(URL.format(year=year))


def parse(raw: bytes) -> list[dict]:
    return [{"date": h["date"], "name": h["name"], "local_name": h.get("localName", ""),
             "global": bool(h.get("global", True))} for h in json.loads(raw)]


def check(rows: list[dict]) -> list[str]:
    return [] if len(rows) >= 10 and all(r["date"] and r["name"] for r in rows) else ["unexpected holiday list"]
