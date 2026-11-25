# Contributing to mortgage-social-media-skills

Thanks for helping. Issues and pull requests are welcome here.

## What lives where

- **This bundle's own files** (README, the three skills, `references/sources.md`,
  `compliance.md`, `calendar.md`, `post-ideas.md`, `compliance-rules.json`,
  `autopilot/trigger.py`, `templates.json`, `tests/test_vertical.py`,
  `evals/cases.py`): change them here in a pull request.
- **Shared files** (listed in `.vertical-core.json`: `lib/`, `scripts/`,
  `autopilot/watch.py`, `tests/test_core.py`, the common references): every
  bundle of the family carries the same copy, maintained upstream by the
  maintainer. Open an issue or a pull request here anyway; the maintainer
  ports the change upstream so every bundle gets it, and the next sync brings
  it back here.

## Compliance rules

A rule change needs a primary source (the statute, the regulation, the
regulator's guidance) with a link and the date you read it. Secondary
sources (blogs, vendor guides) are welcome as leads, not as the source. The
rules are the bundle's reading of public sources, not legal advice; say
whether your change makes a rule stricter or looser and why.

Use the issue template "A rule is wrong or missing": state or jurisdiction,
the citation, the link, the sentence that is wrong.

## Before a pull request

```bash
python3 scripts/check_no_secrets.py
python3 scripts/check_frontmatter.py
python3 scripts/check_markdown_references.py
python3 -m unittest discover -s tests
```

Offline, no keys needed. Behaviour evals (`python3 evals/run_evals.py --list`)
need the `claude` CLI and run against a fake Publora; they are optional for
contributors.

## Style

No em or en dashes in skill text and posts. Every number in a post example
comes from a source. Keep descriptions under 510 characters.
