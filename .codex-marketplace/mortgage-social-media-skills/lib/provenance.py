"""Every number in a post must come from somewhere.

`unsupported_numbers(post, sources)` returns the numbers in the post that do
not appear in any source: the fetched feed data (a dict or list, walked
recursively), the business profile and facts, and the compliance footer the
lint appended. Numbers are compared after normalization: "$1,200" == 1200,
"7.28%" == 7.28, "0.17 points" == 0.17.

Allowed without a source, because they carry no claim:
- small counting numbers 0-12 ("3 things to check");
- years 1900-2100 and day-of-month or clock fragments inside a date or time
  ("Nov 19", "10:30 am", "11/19");
- anything inside a URL, an @handle or a #hashtag.

A rounded figure ("7.3%" for 7.28) is NOT allowed: quote the source exactly.
"""
from __future__ import annotations

import re
from typing import Any, Iterable

NUM = re.compile(r"(?<![\w.])[-+]?\$?(?:\d{1,3}(?:,\d{3})+(?!\d)|\d+)(?:\.\d+)?(?:\s?%|k\b|K\b)?")
URL = re.compile(r"https?://\S+|www\.\S+|[@#][\w.]+", re.I)
MONTHS = (r"(?:january|february|march|april|may|june|july|august|september|october|november|december"
          r"|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec)\b\.?")
DATE_BITS = [
    re.compile(rf"\b{MONTHS}\s+\d{{1,2}}(?:st|nd|rd|th)?\b", re.I),
    re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?:of\s+)?{MONTHS}", re.I),
    re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b|\b\d{1,2}(?::\d{2})?\s?(?:a\.m\.|p\.m\.)", re.I),
    re.compile(r"\b\d{1,3}:\d{1,3}(?:[-\u2013]\d{1,3})?\b"),  # clock times and scripture references (Psalm 119:105)
    re.compile(r"\b(?:de\s+)?\d{1,2}\s+de\s+[a-záéíóú]+", re.I),
]


def _norm(token: str) -> str | None:
    t = token.strip().lower().replace("$", "").replace(",", "").replace("%", "").strip()
    mult = 1
    if t.endswith("k"):
        t, mult = t[:-1], 1000
    t = t.lstrip("+")
    try:
        value = float(t) * mult
    except ValueError:
        return None
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _walk(obj: Any) -> Iterable[str]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(k)
            yield from _walk(v)
    elif isinstance(obj, (list, tuple, set)):
        for v in obj:
            yield from _walk(v)
    elif isinstance(obj, bool) or obj is None:
        return
    elif isinstance(obj, (int, float)):
        yield str(obj)
    else:
        yield str(obj)


def allowed_numbers(sources: Iterable[Any]) -> set[str]:
    allowed: set[str] = set()
    for src in sources:
        for text in _walk(src):
            for tok in NUM.findall(text):
                n = _norm(tok)
                if n is not None:
                    allowed.add(n)
                    allowed.add(n.lstrip("-"))
    return allowed


def _masked(text: str) -> str:
    text = URL.sub(" ", text)
    for rx in DATE_BITS:
        text = rx.sub(" ", text)
    return text


def unsupported_numbers(post: str, sources: Iterable[Any]) -> list[str]:
    allowed = allowed_numbers(sources)
    bad = []
    for tok in NUM.findall(_masked(post)):
        n = _norm(tok)
        if n is None:
            continue
        v = float(n)
        if v.is_integer() and (0 <= abs(v) <= 12 or 1900 <= v <= 2100):
            continue
        if n in allowed or n.lstrip("-") in allowed:
            continue
        bad.append(tok.strip())
    return bad
