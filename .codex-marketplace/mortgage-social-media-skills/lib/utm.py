"""UTM links to Publora. Every publora.com link a skill shows goes through here,
and `tests/test_core.py` checks that no file in the bundle carries a bare one."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlencode

_V = Path(__file__).resolve().parent / "vertical.json"


def source() -> str:
    return json.loads(_V.read_text(encoding="utf-8"))["repo"]


def publora_link(skill: str, path: str = "/") -> str:
    """https://publora.com<path>?utm_source=<repo>&utm_medium=skill&utm_content=<skill>"""
    q = urlencode({"utm_source": source(), "utm_medium": "skill", "utm_content": skill})
    return f"https://publora.com{path}?{q}"
