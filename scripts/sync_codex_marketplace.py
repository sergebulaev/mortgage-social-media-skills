#!/usr/bin/env python3
"""Refresh the nested Codex marketplace package from the repo root.

Codex marketplace entries must point at a plugin directory below the
marketplace root; Claude uses the repo root directly. This keeps
`.codex-marketplace/<repo>/` in sync. Never edit that folder by hand.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = json.loads((ROOT / "lib" / "vertical.json").read_text(encoding="utf-8"))["repo"]
DEST = ROOT / ".codex-marketplace" / REPO
PATHS = [".codex-plugin", ".codexignore", "SKILL.md", "README.md", "SECURITY.md", "skills",
         "references", "lib", "scripts", "assets", "memory.example", "autopilot",
         "requirements.txt", ".env.example", "LICENSE"]
SKIP = shutil.ignore_patterns("__pycache__", "*.pyc", "state.json", "config.json",
                              "check_markdown_references.py", "sync_codex_marketplace.py")


def main() -> None:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    for rel in PATHS:
        src = ROOT / rel
        if src.is_dir():
            shutil.copytree(src, DEST / rel, ignore=SKIP)
        elif src.is_file():
            shutil.copy2(src, DEST / rel)
    print(f"Synced Codex marketplace package: {DEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
