"""Business memory on disk: one folder, markdown only. Optional helper.

Every skill works with plain file tools by following `references/memory.md`;
this module does the same steps with fewer mistakes and never touches the
network. The folder name comes from `lib/vertical.json` (`memory_dir_name`).

Files: profile.md, brand.md, voice.md, rules.md, facts.md, ideas.md,
lessons.md, consent.md. Facts, ideas and lessons are `## X-001` entries with
`- key: value` lines; profile and brand are `- key: value` lines.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

BUNDLE = Path(__file__).resolve().parents[1]
EXAMPLE = BUNDLE / "memory.example"
FILES = ("profile.md", "brand.md", "voice.md", "rules.md", "facts.md", "ideas.md", "lessons.md",
         "consent.md")
ENTRY = re.compile(r"^## (?P<id>[A-Z]+-\d+)(?: · (?P<status>[a-z-]+))?\s*$", re.M)
FIELD = re.compile(r"^-\s+(?P<key>[a-z0-9_ ]+):\s?(?P<value>.*)$", re.M)
SOURCE_USER, SOURCE_DIFF, SOURCE_UNTRUSTED = "user", "diff", "external, untrusted"


def vertical() -> dict:
    return json.loads((BUNDLE / "lib" / "vertical.json").read_text(encoding="utf-8"))


def today() -> str:
    return _dt.date.today().isoformat()


@dataclass
class Location:
    path: Optional[Path]
    source: str
    exists: bool

    def banner(self) -> str:
        if self.path is None:
            return "memory: chat mode (no folder); the updated file is handed back at the end"
        return f"memory: {self.path}" + ("" if self.exists else " (not created yet)")


def _usable(value: Optional[str]) -> bool:
    return bool(value) and "${" not in value and Path(value).expanduser().is_absolute()


def resolve(cwd: Optional[Path] = None, configured: str = "", plugin_data: str = "") -> Location:
    """The documented order: ./<name>/ in the working folder, memory/ in a git
    clone of the bundle, the plugin setting or env var, the plugin data
    folder, else chat mode."""
    v = vertical()
    cwd = Path(cwd or Path.cwd())
    local = cwd / v["memory_dir_name"]
    if local.is_dir():
        return Location(local.resolve(), "workspace", True)
    clone = BUNDLE / "memory"
    if (BUNDLE / ".git").exists() and clone.is_dir():
        return Location(clone, "clone", True)
    for value, source in ((configured, "user_config"), (os.getenv(v["memory_env"], ""), "env")):
        if _usable(value):
            p = Path(value).expanduser()
            return Location(p, source, p.is_dir())
    if _usable(plugin_data):
        p = Path(plugin_data).expanduser() / "memory"
        return Location(p, "plugin_data", p.is_dir())
    return Location(local.resolve(), "new", False)


def init(dest: Path) -> Path:
    """Create memory from memory.example/. Refuses to overwrite."""
    dest = Path(dest)
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError(f"{dest} already has memory; not overwriting")
    shutil.copytree(EXAMPLE, dest, dirs_exist_ok=True)
    return dest


def fields(text: str) -> dict:
    out = {}
    for m in FIELD.finditer(text):
        key = m.group("key").strip().replace(" ", "_")
        value = m.group("value").strip()
        if value and not value.startswith("[") and key not in out:
            out[key] = value
    return out


def load_profile(root: Path) -> dict:
    """profile.md + brand.md as one flat dict. Empty and `[...]` values are
    skipped, so a placeholder can never reach a post."""
    root = Path(root)
    data: dict = {}
    for name in ("brand.md", "profile.md"):
        p = root / name
        if p.is_file():
            data.update(fields(p.read_text(encoding="utf-8")))
    return data


def parse_entries(text: str) -> list[dict]:
    out = []
    marks = list(ENTRY.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[m.end():end]
        entry = {"id": m.group("id"), "status": m.group("status") or ""}
        for f in FIELD.finditer(body):
            entry[f.group("key").strip().replace(" ", "_")] = f.group("value").strip()
        out.append(entry)
    return out


def quote_untrusted(text: str, limit: int = 300) -> str:
    """One line, no headings, in double quotes: it cannot pose as an entry."""
    flat = re.sub(r"\s+", " ", text.replace("#", "")).strip().replace('"', "'")
    return f'"{flat[:limit]}"'


def _next_id(text: str, prefix: str) -> str:
    nums = [int(m.group("id").split("-")[1]) for m in ENTRY.finditer(text) if m.group("id").startswith(prefix + "-")]
    return f"{prefix}-{(max(nums) + 1 if nums else 1):03d}"


def add_fact(root: Path, text: str, source: str, public: bool = True, date: str = "") -> str:
    path = Path(root) / "facts.md"
    body = path.read_text(encoding="utf-8") if path.is_file() else "# Facts\n"
    fid = _next_id(body, "F")
    body = body.rstrip() + (f"\n\n## {fid}\n- text: {text}\n- source: {source}\n- date: {date or today()}\n"
                            f"- public: {'yes' if public else 'no'}\n")
    path.write_text(body, encoding="utf-8")
    return fid


def add_lesson(root: Path, rule: str, evidence: str, source: str = SOURCE_USER) -> str:
    """A candidate lesson. Same rule + same source again: count goes up, and
    for user/diff a second record promotes it. Untrusted text never promotes
    by repetition."""
    path = Path(root) / "lessons.md"
    body = path.read_text(encoding="utf-8") if path.is_file() else "# Lessons\n"
    if source == SOURCE_UNTRUSTED:
        evidence = quote_untrusted(evidence)
    for e in parse_entries(body):
        if e.get("rule", "").lower() == rule.lower() and e.get("source") == source and e["status"] == "candidate":
            count = int(e.get("count", "1")) + 1
            block = re.search(rf"^## {e['id']} · candidate\s*$.*?(?=^## |\Z)", body, re.M | re.S)
            new = re.sub(r"^- count: \d+", f"- count: {count}", block.group(0), flags=re.M)
            new = re.sub(r"^- last: .*$", f"- last: {today()}", new, flags=re.M)
            new = new.rstrip() + f"\n- evidence: {today()}: {evidence}\n\n"
            body = body.replace(block.group(0), new)
            path.write_text(body, encoding="utf-8")
            if count >= 2 and source in (SOURCE_USER, SOURCE_DIFF):
                promote(root, e["id"])
            return e["id"]
    lid = _next_id(body, "L")
    body = body.rstrip() + (f"\n\n## {lid} · candidate\n- rule: {rule}\n- evidence: {today()}: {evidence}\n"
                            f"- source: {source}\n- first: {today()}\n- last: {today()}\n- count: 1\n")
    path.write_text(body, encoding="utf-8")
    return lid


def promote(root: Path, lesson_id: str) -> None:
    root = Path(root)
    lessons = (root / "lessons.md").read_text(encoding="utf-8")
    entry = next((e for e in parse_entries(lessons) if e["id"] == lesson_id), None)
    if not entry:
        raise KeyError(lesson_id)
    lessons = lessons.replace(f"## {lesson_id} · candidate", f"## {lesson_id} · promoted")
    (root / "lessons.md").write_text(lessons, encoding="utf-8")
    rules_path = root / "rules.md"
    rules = rules_path.read_text(encoding="utf-8") if rules_path.is_file() else "# Rules\n"
    if "## Learned" not in rules:
        rules = rules.rstrip() + "\n\n## Learned (promoted from lessons.md)\n"
    rules = rules.rstrip() + f"\n- {entry.get('rule')} ({lesson_id})\n"
    rules_path.write_text(rules, encoding="utf-8")


def consent_for(root: Path, asset: str) -> Optional[dict]:
    """The consent ledger entry for a photo, video or review, or None."""
    path = Path(root) / "consent.md"
    if not path.is_file():
        return None
    for e in parse_entries(path.read_text(encoding="utf-8")):
        if e.get("asset", "").strip().lower() == asset.strip().lower():
            return e
    return None
