"""Data cards for posts: one spec, the best Pixfaro template that exists.

A card spec is a plain dict with a `kind`:

    {"kind": "stat", "value": "6.84%", "label": "30-year fixed, week of Nov 19",
     "source": "Freddie Mac PMMS"}
    {"kind": "table", "title": "...", "rows": [["EB-2 India", "01JAN13", "15FEB13"]],
     "header": ["Category", "November", "December"], "source": "..."}
    {"kind": "checklist", "title": "After the hail", "items": ["...", "..."]}
    {"kind": "event", "title": "Open house", "when": "Sat Nov 22, 1-3 pm",
     "where": "412 Elm St", "cta": "Stop by"}
    {"kind": "quote", "quote": "...", "name": "Pastor Ana"}

The four data templates the design asks for (stat-card, table-card,
checklist-card, event-card) did not exist in Pixfaro's catalog on 2026-11-19.
`plan_render` uses a native template when the live catalog lists one and all
its required slots can be filled, and otherwise falls back: a stat to
`quote-card` (the figure set large, source inside the text), everything else
to `post-card` (text laid out as lines). The fallback is typeset too, so the
numbers stay exactly the numbers from the source.
"""
from __future__ import annotations

from typing import Any, Optional

NATIVE = {"stat": "stat-card", "table": "table-card", "checklist": "checklist-card",
          "event": "event-card", "quote": "quote-card", "post": "post-card"}
POST_CARD_MAX = 900
QUOTE_MAX = 280
NAME_MAX = 60


def _clip(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut.rstrip(",;:") + "…"


def as_lines(spec: dict) -> str:
    """The card as plain lines, for post-card and for the manual path."""
    kind = spec.get("kind")
    out: list[str] = []
    if kind == "stat":
        out = [str(spec["value"]), str(spec.get("label", ""))]
    elif kind == "table":
        if spec.get("title"):
            out.append(spec["title"])
        if spec.get("header"):
            out.append(" | ".join(map(str, spec["header"])))
        out += [" | ".join(map(str, r)) for r in spec.get("rows", [])]
    elif kind == "checklist":
        if spec.get("title"):
            out.append(spec["title"])
        out += [f"✓ {i}" for i in spec.get("items", [])]
    elif kind == "event":
        out = [spec.get("title", ""), spec.get("when", ""), spec.get("where", ""), spec.get("cta", "")]
    elif kind in ("quote", "post"):
        out = [spec.get("quote") or spec.get("text", "")]
    if spec.get("source"):
        out.append(f"Source: {spec['source']}")
    return "\n".join(line for line in out if line)


def _native_slots(spec: dict, template: dict) -> Optional[dict]:
    """Fill a native template's slots by name; None if a required one is missing."""
    slots: dict[str, Any] = {}
    flat = {k: v for k, v in spec.items() if k != "kind"}
    if "items" in flat:
        flat["items"] = "\n".join(flat["items"])
    if "rows" in flat:
        flat["rows"] = "\n".join(" | ".join(map(str, r)) for r in flat["rows"])
    for slot in template.get("slots", []):
        name = slot.get("name")
        if name in flat and flat[name] not in (None, ""):
            value = str(flat[name])
            if slot.get("max"):
                value = _clip(value, int(slot["max"]))
            slots[name] = value
        elif slot.get("required"):
            return None
    return slots or None


def plan_render(spec: dict, catalog: list[dict], *, business_name: str, handle: str = "",
                size: str = "1:1") -> dict:
    """Decide template and slots. Returns {template, slots, size, fallback: bool}."""
    by_id = {t.get("id"): t for t in catalog or []}
    kind = spec.get("kind", "post")
    native = NATIVE.get(kind)
    if native in by_id and kind not in ("quote", "post"):
        slots = _native_slots(spec, by_id[native])
        if slots:
            return {"template": native, "slots": slots, "size": size, "fallback": False}
    name = _clip(business_name or "", NAME_MAX)
    if kind == "stat" and "quote-card" in by_id:
        # One figure reads best set large. quote-card shows the quote and the
        # handle line; the source goes inside the text so it is always visible
        # (checked on a test render 2026-11-19: the name slot was not shown).
        label = str(spec.get("label", ""))
        src = str(spec.get("source", ""))
        text = f"{spec['value']} {label}".strip()
        if src and src.lower() not in label.lower():
            text += f" ({src})"
        slots = {"quote": _clip(text, QUOTE_MAX), "handle": _clip(handle or business_name or "", 40)}
        return {"template": "quote-card", "slots": {k: v for k, v in slots.items() if v},
                "size": size, "fallback": True}
    if kind == "quote" and "quote-card" in by_id:
        slots = {"quote": _clip(spec.get("quote", ""), QUOTE_MAX)}
        if spec.get("name") or name:
            slots["name"] = _clip(spec.get("name") or name, NAME_MAX)
        if handle:
            slots["handle"] = _clip(handle, 40)
        return {"template": "quote-card", "slots": slots, "size": size, "fallback": False}
    slots = {"text": _clip(as_lines(spec), POST_CARD_MAX), "name": name or "Local business"}
    if handle:
        slots["handle"] = _clip(handle, 40)
    return {"template": "post-card", "slots": slots, "size": size,
            "fallback": kind not in ("post",)}


def render(spec: dict, *, business_name: str, handle: str = "", size: str = "1:1",
           client=None, catalog: Optional[list[dict]] = None, style: Any = None) -> dict:
    """Render a card. Returns {url, template, fallback, cost} or raises.

    `client` is a PixfaroClient; `catalog` defaults to the live public list.
    Pass style="brand" only once the brand kit was written (brand.md says
    `pixfaro_brand_kit: yes`); otherwise the template's default look is used."""
    from . import pixfaro
    if catalog is None:
        catalog = pixfaro.list_templates()
    plan = plan_render(spec, catalog, business_name=business_name, handle=handle, size=size)
    client = client or pixfaro.PixfaroClient()
    out = client.render(plan["template"], plan["slots"], size=plan["size"], style=style)
    return {"url": out.get("url"), "id": out.get("id"), "cost": out.get("cost"),
            "template": plan["template"], "fallback": plan["fallback"]}
