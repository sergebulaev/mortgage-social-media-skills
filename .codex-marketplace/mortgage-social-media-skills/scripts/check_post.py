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

Exit code: 0 PASS, 1 FAIL, 2 REVIEW (flags a human must look at). The exit
code does not change with who asks or how urgent it is.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import compliance, memory, provenance, style  # noqa: E402


def run(text: str, *, profile: dict, sources: list, platform: str = "", language: str = "",
        fix: bool = False) -> dict:
    report = (compliance.autofix if fix else compliance.check)(
        text, profile=profile, platform=platform, language=language)
    final = report.text
    numbers = provenance.unsupported_numbers(final, [*sources, profile])
    voice = style.lint(final, platform)
    verdict = report.verdict
    if numbers or not voice["ok"]:
        verdict = "FAIL"
    return {"verdict": verdict, "text": final, "compliance": report.summary(),
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
              language=args.language, fix=args.fix)
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(out["compliance"])
        if out["unsupported_numbers"]:
            print("Numbers with no source: " + ", ".join(out["unsupported_numbers"]))
        for f in out["voice"]["strict"]:
            print(f"Voice: {f['code']} ({f['match']}): {f['why']}")
        for f in out["voice"]["soft"]:
            print(f"Voice (soft): {f['code']}: {f['why']}")
        print(f"VERDICT: {out['verdict']}")
        if args.fix and out["applied"]:
            print("\n--- fixed text ---\n" + out["text"])
    return {"PASS": 0, "FAIL": 1, "REVIEW": 2}[out["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
