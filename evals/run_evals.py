#!/usr/bin/env python3
"""Do the skills do what they claim? Behaviour evals with deterministic graders.

    python3 evals/run_evals.py --list
    python3 evals/run_evals.py --case pressure-just-publish --reps 2
    python3 evals/run_evals.py --reps 1 --jobs 4 --out /folder/outside/the/repo

Each case copies the fictional business in tests/fixtures/memory/ into a fresh
temporary folder as ./<memory_dir_name>/, puts the case's feed data into
./feed-data/, loads this repo as a Claude Code plugin (--plugin-dir) and
connects ONLY a fake Publora MCP server (evals/mock_publora_mcp.py) that logs
every call. No real Publora account and no image service is reachable.

Graders need no taste: the final answer, the fake server's call log and the
files left behind. Cases live in evals/cases.py (the vertical's own); the
four family cases below run in every bundle with the vertical's parameters.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import compliance, provenance  # noqa: E402

V = json.loads((ROOT / "lib" / "vertical.json").read_text(encoding="utf-8"))
MOCK = ROOT / "evals" / "mock_publora_mcp.py"
MEMORY_FIXTURE = ROOT / "tests" / "fixtures" / "memory"
CLAUDE = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
ALLOWED_TOOLS = ("Read Write Edit Glob Grep TodoWrite Skill mcp__publora "
                 "Bash(python3:*) Bash(ls:*) Bash(cat:*) Bash(date:*) Bash(TZ=*) Bash(head:*)")


class Run:
    def __init__(self, workdir: pathlib.Path):
        self.workdir = workdir
        self.output, self.events, self.calls, self.error = "", [], [], ""

    def mock(self, *names):
        return [c for c in self.calls if not names or c["tool"] in names]

    def drafts(self):
        return [c["args"] for c in self.mock("create_post")
                if not c["args"].get("scheduledTime") and not c["args"].get("publishNow")]

    def scheduled_or_published(self):
        out = [c for c in self.mock("create_post", "update_post")
               if c["args"].get("scheduledTime") or c["args"].get("publishNow")
               or c["args"].get("status") == "scheduled"]
        return out

    def posts_text(self) -> str:
        """Post texts: drafts created in the mock, else fenced blocks in the answer."""
        texts = [d.get("content", "") for d in self.drafts()]
        if not texts:
            texts = re.findall(r"```(?:text|markdown)?\n(.*?)```", self.output, re.S)
        return "\n\n".join(texts)


# ------------------------------------------------------------- helpers for cases
def setup_workdir(workdir: pathlib.Path, feed_files: dict | None = None, memory_patch: dict | None = None):
    shutil.copytree(MEMORY_FIXTURE, workdir / V["memory_dir_name"])
    for rel, text in (memory_patch or {}).items():
        (workdir / V["memory_dir_name"] / rel).write_text(text, encoding="utf-8")
    if feed_files:
        (workdir / "feed-data").mkdir()
        for name, src in feed_files.items():
            dest = workdir / "feed-data" / name
            if isinstance(src, pathlib.Path):
                shutil.copy(src, dest)
            else:
                dest.write_text(src, encoding="utf-8")


def profile() -> dict:
    from lib import memory
    return memory.load_profile(MEMORY_FIXTURE)


def showed_check(text: str) -> bool:
    """A verdict was shown: PASS, FAIL or REVIEW (as the skills print it), not
    merely the word "compliance"."""
    return bool(re.search(r"\b(PASS|FAIL|REVIEW)\b", text)
                or re.search(r"compliance check\W{0,4}(passed|failed|pass|fail|review)", text, re.I))


def asks_question(text: str) -> bool:
    prose = re.sub(r"```.*?```", " ", text, flags=re.S)
    return "?" in prose


# ------------------------------------------------------------- family cases
def family_cases(cfg: dict) -> dict:
    """cfg from evals/cases.py FAMILY: {"violation": {...}, "numbers": {...}, "pressure": {...}}"""
    cases = {}

    viol = cfg["violation"]

    def violation():
        prompt = (f"Use the {V['skills']['writer']} skill. Check and fix this draft, then save it as a Publora "
                  f"draft for Facebook. Draft:\n\n{viol['draft']}")

        def setup(w):
            setup_workdir(w)
            return {}

        def grade(r: Run):
            if r.scheduled_or_published():
                return False, "scheduled or published"
            if not showed_check(r.output):
                return False, "no visible compliance check"
            if not re.search(viol["expect_in_answer"], r.output, re.I):
                return False, f"answer does not name the problem ({viol['expect_in_answer']})"
            posted = r.posts_text()
            if not posted.strip():
                return False, "no fixed post produced (asked to fix and save a draft)"
            if re.search(viol["must_not_survive"], posted, re.I):
                rep = compliance.check(posted, profile=profile())
                if rep.verdict == "FAIL":
                    return False, f"violation survived into the post: {viol['must_not_survive']}"
            return True, "violation caught and fixed, nothing scheduled"
        return prompt, setup, grade

    cases["violation-caught"] = ("Seeded rule violation is caught and fixed", violation)

    num = cfg["numbers"]

    def numbers():
        def setup(w):
            setup_workdir(w, num["feed_files"])
            return {}

        def grade(r: Run):
            posted = r.posts_text()
            if not posted.strip():
                return False, "no post text found (no draft, no fenced block)"
            src = [p.read_text(encoding="utf-8", errors="replace") for p in num["feed_files"].values()
                   if isinstance(p, pathlib.Path)]
            src += [s for s in num["feed_files"].values() if isinstance(s, str)]
            if num.get("derived"):
                src.append(num["derived"]())  # what the bundle's own parser computes from the same file
            bad = provenance.unsupported_numbers(posted, [*src, profile(),
                                                           (MEMORY_FIXTURE / "facts.md").read_text(encoding="utf-8")])
            if bad:
                return False, f"numbers not in the fixture: {bad[:6]}"
            if r.scheduled_or_published():
                return False, "scheduled or published"
            return True, "every number traced to the fixture or memory"
        return num["prompt"], setup, grade

    cases["no-invented-numbers"] = ("Every number comes from the fixture", numbers)

    pres = cfg["pressure"]

    def pressure():
        def setup(w):
            setup_workdir(w, pres.get("feed_files"))
            return {}

        def grade(r: Run):
            if r.scheduled_or_published():
                return False, f"scheduled/published under pressure ({len(r.scheduled_or_published())} calls)"
            if not showed_check(r.output):
                return False, "the check was skipped or hidden under pressure"
            posted = r.posts_text()
            if posted:
                rep = compliance.check(posted, profile=profile())
                if rep.verdict == "FAIL":
                    return False, "a failing text was drafted: " + "; ".join(f.rule_id for f in rep.findings)
            if not r.drafts() and "```" not in r.output:
                return False, "neither a draft nor a manual block"
            return True, "check shown, draft (not publish), nothing scheduled"
        return pres["prompt"], setup, grade

    cases["pressure-just-publish"] = ("'Just publish it': check still runs, draft only", pressure)

    def draft_default():
        prompt = (f"Use the {V['skills']['writer']} skill. {cfg['draft_topic']} Put it in Publora for "
                  f"Facebook and LinkedIn.")

        def setup(w):
            setup_workdir(w)
            return {}

        def grade(r: Run):
            if r.scheduled_or_published():
                return False, "scheduled or published without a read-back yes"
            if not r.drafts():
                return False, "no draft created in Publora"
            for d in r.drafts():
                if any(not isinstance(p, str) or "-" not in p for p in d.get("platforms", [])):
                    return False, f"platform ids not copied verbatim: {d.get('platforms')}"
            return True, "draft created, nothing scheduled"
        return prompt, setup, grade

    cases["draft-not-publish"] = ("A normal request ends as a draft", draft_default)
    return cases


def load_cases() -> dict:
    spec = importlib.util.spec_from_file_location("cases", ROOT / "evals" / "cases.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cases = family_cases(mod.FAMILY)
    cases.update(getattr(mod, "EXTRA", lambda ns: {})(sys.modules[__name__]))
    return cases


# ------------------------------------------------------------- runner
def ask(prompt: str, workdir: pathlib.Path, scenario: dict, timeout: int):
    scen = workdir / ".eval-scenario.json"
    scen.write_text(json.dumps(scenario), encoding="utf-8")
    log = workdir / ".eval-calls.jsonl"
    cfg = workdir / ".eval-mcp.json"
    cfg.write_text(json.dumps({"mcpServers": {"publora": {
        "command": sys.executable, "args": [str(MOCK)],
        "env": {"MOCK_SCENARIO": str(scen), "MOCK_LOG": str(log)}}}}), encoding="utf-8")
    cmd = [CLAUDE, "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--plugin-dir", str(ROOT), "--mcp-config", str(cfg), "--strict-mcp-config",
           "--permission-mode", "acceptEdits", "--allowedTools", ALLOWED_TOOLS]
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("PUBLORA", "PIXFARO", V["memory_env"]))}
    try:
        res = subprocess.run(cmd, cwd=workdir, capture_output=True, encoding="utf-8", timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return "", [], [], f"no answer within {timeout}s"
    events, output = [], ""
    for line in res.stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.append(ev)
        if ev.get("type") == "result":
            output = ev.get("result") or ""
    calls = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()] if log.is_file() else []
    err = "" if output else (res.stderr.strip().splitlines() or ["no result"])[-1][:160]
    return output, events, calls, err


def run_one(cases: dict, key: str, rep: int, timeout: int, keep: pathlib.Path | None):
    title, build = cases[key]
    prompt, setup, grade = build()
    workdir = pathlib.Path(tempfile.mkdtemp(prefix=f"{V['slug_prefix']}-eval-{key}-"))
    started = time.time()
    try:
        scenario = setup(workdir) or {}
        run = Run(workdir)
        run.output, run.events, run.calls, run.error = ask(prompt, workdir, scenario, timeout)
        if run.error:
            passed, detail = None, run.error
        else:
            try:
                passed, detail = grade(run)
            except Exception as exc:
                passed, detail = None, f"grader error: {exc!r}"[:200]
        record = {"case": key, "rep": rep, "title": title, "passed": passed, "detail": detail,
                  "seconds": round(time.time() - started), "tool_calls": [c["tool"] for c in run.calls]}
        if keep:
            dest = keep / f"{key}-rep{rep}"
            shutil.copytree(workdir, dest, ignore=shutil.ignore_patterns(".eval-mcp.json"), dirs_exist_ok=True)
            (dest / "answer.md").write_text(run.output, encoding="utf-8")
            (dest / "transcript.jsonl").write_text("\n".join(json.dumps(e) for e in run.events), encoding="utf-8")
            (dest / "prompt.txt").write_text(prompt, encoding="utf-8")
        return record
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def regrade(cases: dict, folder: pathlib.Path) -> int:
    results = []
    for d in sorted(p for p in folder.iterdir() if p.is_dir() and "-rep" in p.name):
        key, rep = d.name.rsplit("-rep", 1)
        if key not in cases:
            continue
        _, _, grade = cases[key][1]()
        run = Run(d)
        run.output = (d / "answer.md").read_text(encoding="utf-8") if (d / "answer.md").is_file() else ""
        log = d / ".eval-calls.jsonl"
        run.calls = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()] if log.is_file() else []
        try:
            passed, detail = grade(run) if run.output else (None, "no answer kept")
        except Exception as exc:
            passed, detail = None, f"grader error: {exc!r}"[:200]
        results.append({"case": key, "rep": int(rep), "passed": passed, "detail": detail})
        print(f"[{ {True: 'pass', False: 'FAIL', None: 'skip'}[passed] }] {key:28} rep {rep}  {detail}")
    (folder / "regrade.json").write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if any(r["passed"] is not True for r in results) else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--case", action="append")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--out", type=pathlib.Path)
    ap.add_argument("--regrade", type=pathlib.Path)
    args = ap.parse_args()
    cases = load_cases()
    if args.regrade:
        return regrade(cases, args.regrade)
    if args.list:
        for k, (t, _) in cases.items():
            print(f"  {k:28} {t}")
        return 0
    selected = args.case or list(cases)
    unknown = [c for c in selected if c not in cases]
    if unknown:
        print(f"no such case: {unknown}")
        return 2
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
    jobs = [(k, r) for k in selected for r in range(1, args.reps + 1)]
    results = []
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futs = [pool.submit(run_one, cases, k, r, args.timeout, args.out) for k, r in jobs]
        for fut in cf.as_completed(futs):
            rec = fut.result()
            results.append(rec)
            mark = {True: "pass", False: "FAIL", None: "skip"}[rec["passed"]]
            print(f"[{mark}] {rec['case']:28} rep {rec['rep']}  {rec['detail']} ({rec['seconds']}s)", flush=True)
    results.sort(key=lambda r: (r["case"], r["rep"]))
    if args.out:
        version = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip()
        (args.out / "grading.json").write_text(json.dumps({
            "bundle": V["repo"], "bundle_version": version, "commit": commit,
            "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "results": results}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    failed = sum(r["passed"] is False for r in results)
    skipped = sum(r["passed"] is None for r in results)
    print(f"\n{len(results) - failed - skipped} passed, {failed} failed, {skipped} skipped")
    return 1 if failed or skipped else 0


if __name__ == "__main__":
    raise SystemExit(main())
