#!/usr/bin/env python3
"""Check Markdown references declared by skill documents.

Every backticked path ending in ``.md`` in the root ``SKILL.md``, the shared
``references/`` tree, and everything under ``skills/`` must resolve either
relative to the citing document (bare sibling ``post-audit.md``, skill-local
``references/X.md`` / ``sub-skills/X.md``, nested ``../../../references/X.md``)
or relative to the repository root (``skills/<skill>/SKILL.md``, ``README.md``).
"""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REFERENCE = re.compile(r"`((?:\.\.?/)*[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)*\.md)(?:#[^`]*)?`")


def documents() -> list[Path]:
    """Root SKILL.md, shared root references, and everything under skills/."""
    found = [ROOT / "SKILL.md"] if (ROOT / "SKILL.md").is_file() else []
    found += sorted((ROOT / "references").rglob("*.md"))
    found += sorted(SKILLS.rglob("*.md"))
    return found


MEMORY = ROOT / "memory.example"
try:
    import json
    MEMORY_NAME = json.loads((ROOT / "lib" / "vertical.json").read_text(encoding="utf-8"))["memory_dir_name"]
except (OSError, ValueError, KeyError):
    MEMORY_NAME = ""


def resolves(document: Path, ref: str) -> bool:
    """Relative to the document, to the repo root, or a business memory file
    (they ship as memory.example/<name>; `<memory>/plan-*.md` and the chat-mode
    `<memory>.md` exist only on the user's side)."""
    if MEMORY_NAME and (ref.startswith(MEMORY_NAME + "/") or ref == MEMORY_NAME + ".md"):
        return True
    return ((document.parent / ref).resolve().is_file() or (ROOT / ref).resolve().is_file()
            or ("/" not in ref and (MEMORY / ref).is_file()))


def main() -> None:
    broken: list[str] = []

    for document in documents():
        text = document.read_text(encoding="utf-8")
        for match in REFERENCE.finditer(text):
            ref = match.group(1)
            if "://" in ref or ref.startswith("/"):
                continue
            if not resolves(document, ref):
                broken.append(f"{document.relative_to(ROOT)}: {ref}")

    if broken:
        raise SystemExit("Broken Markdown references:\n" + "\n".join(broken))

    print("All Markdown references resolve.")


if __name__ == "__main__":
    main()
