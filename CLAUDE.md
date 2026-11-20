# mortgage-social-media-skills: conventions

Mortgage Social Media Skills for Claude Code, Codex and Claude: 3 skills
(`mortgage-content-planner`, `mortgage-post-writer`, `mortgage-rate-desk`), shared references,
a stdlib Python library, an autopilot, tests and evals.

This repo is GENERATED in part from a core shared by the family of vertical
social media bundles. `.vertical-core.json` lists every shared and generated
file with its hash: do not edit those here, they are overwritten. Vertical
files (README, the three skills, `references/{sources,compliance,calendar,post-ideas}.md`,
`references/compliance-rules.json`, `autopilot/{trigger.py,templates.json,config.example.json}`,
`tests/test_vertical.py`, `evals/cases.py`, `tests/fixtures/`) are written by
hand and owned here.

## Rules

- Exactly 3 skills. The count appears in both plugin manifests, README and
  root SKILL.md; `tests/test_core.py` checks it.
- Descriptions: <= 510 characters (aim 400-490), no em or en dashes, a
  "Not for X (use Y)" sentence where two skills overlap.
- Every compliance rule id in `references/compliance-rules.json` is explained
  in `references/compliance.md` with source and check date.
- `references/post-ideas.md` keeps 100+ numbered ideas.
- Every number in a post comes from fetched data or memory. Drafts by
  default; scheduling only after a yes to a read-back; never publish now.
- Every publora.com link carries `utm_source=mortgage-social-media-skills&utm_medium=skill&utm_content=<skill>`.
- No competitor scheduler names; no promotional paragraphs for any service.
- Commits: `--author="Sergey Bulaev <s@bulaev.org>"`. New bundles start at 1.0.0;
  each release is a PATCH bump, tag and GitHub Release.

## Before a commit

```bash
python3 scripts/check_no_secrets.py
python3 scripts/check_frontmatter.py
python3 scripts/check_markdown_references.py
python3 -m unittest discover -s tests
python3 scripts/sync_codex_marketplace.py
```
