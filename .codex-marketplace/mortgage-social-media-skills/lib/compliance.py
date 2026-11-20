"""Deterministic compliance lint for a post, driven by JSON rules.

Rules live in `references/compliance-rules.json` (the vertical's own) plus
`lib/rules_common.json` (FTC reviews and endorsements, music, fees; every
vertical). `references/compliance.md` is the human half: the same rule ids
with the source, an example and a fix.

A rule:

    {"id": "REGZ-APR", "level": "fix",
     "title": "Rate or trigger term without APR",
     "if_any": ["\\b\\d+(\\.\\d+)?\\s?%\\s*(rate|fixed)", "\\$[\\d,]+\\s*/\\s*mo"],
     "unless_any": ["\\bAPR\\b"],         # skip when any of these is present
     "unless_all": ["APR", "down", "term"], # skip only when ALL are present
     "unless_scope": "sentence",            # optional: look for unless_* in the triggering sentence only
     "append": "{apr_disclosure}",
     "states": ["*"], "states_except": ["TX"], "languages": ["en", "es"],
     "unless_profile": {"service_charge": ["", "none", "no"]},  # skip when the profile
                                            # field (lowercased) is one of these values
     "message": "...", "source": "12 CFR 1026.24(c),(d)", "checked": "2026-11-19"}

Levels:
- block: the post must be rewritten; nothing may go out with it.
- fix:   a required element is missing. `autofix` appends `append` when every
         {placeholder} is filled from the profile, else it stays a failure.
- flag:  a human must look (Fair Housing words, a minor in a photo...).

Verdict: FAIL if any block or fix finding remains, REVIEW if only flags,
PASS otherwise. The verdict never depends on who is asking or how urgent it
is: "just publish it" changes nothing here.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

ROOT = Path(__file__).resolve().parents[1]
COMMON_RULES = Path(__file__).resolve().parent / "rules_common.json"
VERTICAL_RULES = ROOT / "references" / "compliance-rules.json"
LEVELS = ("block", "fix", "flag")


@dataclass
class Finding:
    rule_id: str
    level: str
    title: str
    message: str
    match: str = ""
    source: str = ""
    fixable: bool = False
    missing_profile: list = field(default_factory=list)

    def line(self) -> str:
        where = f' ("{self.match}")' if self.match else ""
        extra = f" Missing in profile: {', '.join(self.missing_profile)}." if self.missing_profile else ""
        return f"[{self.level.upper()}] {self.rule_id}: {self.title}{where}. {self.message}{extra} ({self.source})"


@dataclass
class Report:
    verdict: str
    findings: list
    text: str
    applied: list = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"Compliance check: {self.verdict}"]
        lines += ["  fixed: " + a for a in self.applied]
        lines += ["  " + f.line() for f in self.findings]
        if not self.findings and not self.applied:
            lines.append("  no rule triggered")
        return "\n".join(lines)


def load_rules(paths: Optional[Iterable[Path]] = None) -> list[dict]:
    rules: list[dict] = []
    for path in paths or (COMMON_RULES, VERTICAL_RULES):
        path = Path(path)
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        rules += data["rules"] if isinstance(data, dict) else data
    ids = [r["id"] for r in rules]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"duplicate rule ids: {sorted(dupes)}")
    for r in rules:
        if r.get("level") not in LEVELS:
            raise ValueError(f"{r.get('id')}: level must be one of {LEVELS}")
    return rules


def normalize(text: str) -> str:
    """Fold look-alike characters so a rule cannot be dodged with a curly
    apostrophe, a non-breaking space or a zero-width joiner."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[​-‍⁠﻿]", "", text)
    return text.replace("’", "'").replace("‘", "'").replace(" ", " ")


def _applies(rule: dict, state: str, language: str, platform: str, profile: Optional[dict] = None) -> bool:
    for key, values in (rule.get("unless_profile") or {}).items():
        if str((profile or {}).get(key, "")).strip().lower() in {v.lower() for v in values}:
            return False
    states = rule.get("states") or ["*"]
    if "*" not in states and (state or "").upper() not in {s.upper() for s in states}:
        return False
    if (state or "").upper() in {s.upper() for s in rule.get("states_except", [])}:
        return False
    langs = rule.get("languages")
    if langs and language and language not in langs:
        return False
    plats = rule.get("platforms")
    if plats and platform not in plats:
        return False  # a platform-scoped rule runs only when that platform is named
    return True


def _search(patterns: Iterable[str], text: str):
    for p in patterns or []:
        m = re.search(p, text, re.I | re.M)
        if m:
            return m
    return None


def _fill(template: str, profile: dict) -> tuple[str, list]:
    missing = [k for k in re.findall(r"\{(\w+)\}", template) if not str(profile.get(k, "")).strip()]
    if missing:
        return "", missing
    return template.format(**{k: str(v).strip() for k, v in profile.items()}), []


def check(text: str, *, profile: Optional[dict] = None, rules: Optional[list] = None,
          platform: str = "", language: str = "") -> Report:
    profile = profile or {}
    rules = load_rules() if rules is None else rules
    state = str(profile.get("state", ""))
    language = language or str(profile.get("language", "en"))
    norm = normalize(text)
    findings = []
    for rule in rules:
        if not _applies(rule, state, language, platform, profile):
            continue
        if rule.get("if_any"):
            matches = [m for p in rule["if_any"] for m in re.finditer(p, norm, re.I | re.M)]
            if not matches:
                continue
        else:
            matches = [None]
        trigger = None
        for m in matches:
            # unless_* are looked up in the whole post, or only in the sentence of
            # THIS match when the rule says "unless_scope": "sentence" (so "Never
            # give ibuprofen" cannot excuse "Try Benadryl" two sentences later).
            scope = norm
            if m is not None and rule.get("unless_scope") == "sentence":
                start = max(norm.rfind(c, 0, m.start()) for c in ".!?\n") + 1
                ends = [k for k in (norm.find(c, m.end()) for c in ".!?\n") if k != -1]
                scope = norm[start:(min(ends) + 1) if ends else len(norm)]
            if _search(rule.get("unless_any"), scope):
                continue
            if rule.get("unless_all") and all(_search([rx], scope) for rx in rule["unless_all"]):
                continue
            trigger = m if m is not None else True
            break
        if trigger is None:
            continue
        if trigger is True:
            trigger = None
        missing = []
        fixable = False
        if rule["level"] == "fix" and rule.get("append"):
            _, missing = _fill(rule["append"], profile)
            fixable = not missing
        findings.append(Finding(rule["id"], rule["level"], rule.get("title", ""), rule.get("message", ""),
                                trigger.group(0) if trigger else "", rule.get("source", ""), fixable, missing))
    return Report(_verdict(findings), findings, text)


def _verdict(findings: list) -> str:
    if any(f.level in ("block", "fix") for f in findings):
        return "FAIL"
    if findings:
        return "REVIEW"
    return "PASS"


def autofix(text: str, *, profile: Optional[dict] = None, rules: Optional[list] = None,
            platform: str = "", language: str = "") -> Report:
    """Append every fillable required element, then check again.

    Only `fix` rules with an `append` template are touched. A `block` is never
    auto-fixed: rewriting a guarantee or a deductible offer is a judgment the
    writer makes, and the report says so."""
    profile = profile or {}
    rules = load_rules() if rules is None else rules
    by_id = {r["id"]: r for r in rules}
    applied, out = [], text.rstrip()
    # Repeat until nothing changes: an appended line can itself trigger or
    # satisfy another rule, and the final verdict must describe the final text.
    for _ in range(4):
        report = check(out, profile=profile, rules=rules, platform=platform, language=language)
        changed = False
        for f in report.findings:
            if f.level == "fix" and f.fixable:
                addition, _ = _fill(by_id[f.rule_id]["append"], profile)
                if addition and addition not in out:
                    out = f"{out}\n\n{addition}"
                    applied.append(f"{f.rule_id}: appended \"{addition}\"")
                    changed = True
        if not changed:
            break
    second = check(out, profile=profile, rules=rules, platform=platform, language=language)
    second.applied = applied
    return second
