"""Read `.env` without python-dotenv (stdlib only).

Only the bundle's own credentials and settings are loaded, and a variable that
is already set in the environment always wins. Nothing here executes anything.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VARIABLES = (
    "PUBLORA_API_KEY", "PUBLORA_PLATFORMS",
    "PIXFARO_KEY", "PIXFARO_TOKEN", "PIXFARO_API_KEY",
    "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL",
)
_loaded = False


def _candidates() -> list[Path]:
    out = []
    cur = Path.cwd()
    for d in [cur, *cur.parents]:
        if (d / ".env").is_file():
            out.append(d / ".env")
            break
    if (ROOT / ".env") not in out:
        out.append(ROOT / ".env")
    return out


def load_env(force: bool = False) -> None:
    global _loaded
    if _loaded and not force:
        return
    for path in _candidates():
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip().removeprefix("export ").strip()
            if key in VARIABLES:
                os.environ.setdefault(key, value.strip().strip("\"'"))
    _loaded = True


def pixfaro_key() -> str | None:
    load_env()
    return os.getenv("PIXFARO_KEY") or os.getenv("PIXFARO_TOKEN") or os.getenv("PIXFARO_API_KEY")
