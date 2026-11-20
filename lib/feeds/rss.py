"""Generic RSS 2.0 / Atom reader (stdlib xml)."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from .. import _http

ATOM = "{http://www.w3.org/2005/Atom}"
MEDIA = "{http://search.yahoo.com/mrss/}"  # YouTube puts the description in media:group


def fetch(url: str) -> bytes:
    return _http.get_bytes(url, headers={"Accept": "application/rss+xml, application/atom+xml, application/xml"})


def _date(text: str) -> str:
    if not text:
        return ""
    try:
        return parsedate_to_datetime(text).date().isoformat()
    except (TypeError, ValueError):
        m = re.match(r"\d{4}-\d{2}-\d{2}", text.strip())
        return m.group(0) if m else text.strip()


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip()


def parse(raw: bytes) -> list[dict]:
    root = ET.fromstring(raw)
    items = []
    for it in root.iter("item"):
        items.append({"title": _clean(it.findtext("title")), "link": (it.findtext("link") or "").strip(),
                      "date": _date(it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date")),
                      "summary": _clean(it.findtext("description"))[:600],
                      "guid": (it.findtext("guid") or it.findtext("link") or "").strip()})
    for it in root.iter(ATOM + "entry"):
        link = it.find(ATOM + "link")
        items.append({"title": _clean(it.findtext(ATOM + "title")),
                      "link": link.get("href", "") if link is not None else "",
                      "date": _date(it.findtext(ATOM + "published") or it.findtext(ATOM + "updated")),
                      "summary": _clean(it.findtext(ATOM + "summary")
                                        or it.findtext(f"{MEDIA}group/{MEDIA}description") or "")[:600],
                      "guid": it.findtext(ATOM + "id") or ""})
    return items


def check(items: list[dict]) -> list[str]:
    if not items:
        return ["no items"]
    missing = [k for k in ("title", "link", "date") if not items[0].get(k)]
    return [f"first item has no {k}" for k in missing]
