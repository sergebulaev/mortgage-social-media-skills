#!/usr/bin/env python3
"""Check one post before it becomes a draft: compliance, numbers, voice.

    python3 scripts/check_post.py post.txt --memory ./<v>-memory \
        --source data.json --platform facebook [--fix] [--json]

- compliance: the vertical's rules plus the common ones (`lib/compliance.py`);
  with --fix, required footers (license number, NMLS, APR block...) that the
  profile can fill are appended and the fixed text is printed.
- numbers: every number must appear in --source (feed data the skill fetched,
  any number of files) or in the business memory (`lib/provenance.py`).
- voice: enumerated AI tells and the platform length (`lib/style.py`).
- length: with --platform and --fix, a text over that network's limit is cut
  to a version that fits (`lib/platforms.py`: opening line, link lines and
  every required line kept); if the required lines alone do not fit, the
  verdict is FAIL and there is no draft for that network. Run it once per
  network you post to: X 280, Bluesky 300, Threads and Mastodon 500.
- main fact: --must "7.21%" (repeatable) names what the post is about (the
  rate and its change, the hail size and the place, the product). A version
  without it is FAIL: write the short version from the fact, do not let the
  cut drop it (a rate post cut to "the survey is out" said nothing).

Exit code: 0 PASS, 1 FAIL, 2 REVIEW (flags a human must look at). The exit
code does not change with who asks or how urgent it is.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import compliance, memory, platforms, provenance, style  # noqa: E402


CONSENT_LINE = re.compile(r"(shared |posted )?with (their|his|her|the (patient|client|owner|member|family)'?s?) "
                          r"(written )?(permission|consent)|con (su )?(permiso|consentimiento)", re.I)


def consent_problem(text: str, memory_root, platform: str) -> str:
    """A post may claim consent only if consent.md holds a live entry for this
    network. The rules accept the consent line as proof; this is the check
    that the line is true."""
    if not CONSENT_LINE.search(text):
        return ""
    if memory_root is None:
        return "the post says consent was given, but no memory folder was given to check consent.md"
    path = Path(memory_root) / "consent.md"
    entries = memory.parse_entries(path.read_text(encoding="utf-8")) if path.is_file() else []
    today = dt.date.today().isoformat()
    for e in entries:
        agreed = e.get("agreed", "").lower().startswith("yes")
        live = not e.get("expires") or e.get("expires", "") >= today
        scope = e.get("scope", "").lower()
        if agreed and live and (not platform or not scope or platform.lower() in scope or "all" in scope):
            return ""
    return (f"the post says consent was given, but consent.md has no agreed, unexpired entry covering "
            f"{platform or 'this network'}")


def run(text: str, *, profile: dict, sources: list, platform: str = "", language: str = "",
        fix: bool = False, memory_root=None, must=()) -> dict:
    fit_note = ""
    if fix and platform:
        fitted, fit_note = platforms.fit(
            text, platform.lower(), finish=lambda t: compliance.autofix(
                t, profile=profile, platform=platform, language=language).text)
        if fitted is not None:
            fit_note = ""
            if fitted != compliance.autofix(text, profile=profile, platform=platform, language=language).text:
                text = fitted
                fit_note = f"shortened to fit {platform}"
    report = (compliance.autofix if fix else compliance.check)(
        text, profile=profile, platform=platform, language=language)
    final = report.text
    numbers = provenance.unsupported_numbers(final, [*sources, profile])
    voice = style.lint(final, platform)
    verdict = report.verdict
    consent = consent_problem(final, memory_root, platform)
    if consent and verdict == "PASS":
        verdict = "REVIEW"
    if numbers or not voice["ok"]:
        verdict = "FAIL"
    if fit_note and not fit_note.startswith("shortened"):
        verdict = "FAIL"  # the required lines do not fit this network
    lost = [m for m in must if m not in final]
    if lost:
        verdict = "FAIL"  # the version lost what the post is about
    return {"verdict": verdict, "text": final, "compliance": report.summary(), "consent": consent,
            "length": fit_note, "missing_fact": lost,
            "compliance_verdict": report.verdict, "applied": report.applied,
            "unsupported_numbers": numbers, "voice": voice}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("post", help="file with the post text, or - for stdin")
    ap.add_argument("--memory", type=Path, help="business memory folder (profile.md, brand.md, facts.md)")
    ap.add_argument("--source", type=Path, action="append", default=[], help="feed data (JSON or text)")
    ap.add_argument("--platform", default="")
    ap.add_argument("--language", default="")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--must", action="append", default=[],
                    help="the post's main fact (a number, a place, a name); every version must keep it")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    text = sys.stdin.read() if args.post == "-" else Path(args.post).read_text(encoding="utf-8")
    profile, sources = {}, []
    if args.memory:
        profile = memory.load_profile(args.memory)
        facts = args.memory / "facts.md"
        if facts.is_file():
            sources.append(facts.read_text(encoding="utf-8"))
    for src in args.source:
        raw = src.read_text(encoding="utf-8")
        try:
            sources.append(json.loads(raw))
        except ValueError:
            sources.append(raw)
    out = run(text, profile=profile, sources=sources, platform=args.platform,
              language=args.language, fix=args.fix, memory_root=args.memory, must=args.must)
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(out["compliance"])
        if out["consent"]:
            print("Consent: " + out["consent"])
        if out["length"]:
            print("Length: " + out["length"])
        if out["missing_fact"]:
            print("Main fact missing (write the short version from it): " + ", ".join(out["missing_fact"]))
        if out["unsupported_numbers"]:
            print("Numbers with no source: " + ", ".join(out["unsupported_numbers"]))
        for f in out["voice"]["strict"]:
            print(f"Voice: {f['code']} ({f['match']}): {f['why']}")
        for f in out["voice"]["soft"]:
            print(f"Voice (soft): {f['code']}: {f['why']}")
        print(f"VERDICT: {out['verdict']}")
        if args.fix and (out["applied"] or out["length"].startswith("shortened")):
            print("\n--- fixed text ---\n" + out["text"])
    return {"PASS": 0, "FAIL": 1, "REVIEW": 2}[out["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
