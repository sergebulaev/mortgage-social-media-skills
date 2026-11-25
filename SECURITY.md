# Security

## Reporting

Please report a vulnerability privately: on this repo's **Security** tab,
**Report a vulnerability** (GitHub private vulnerability reporting). Please
do not open a public issue for it.

## What this bundle can touch

- **Network:** the public feeds listed in `references/sources.md`; Publora
  (`api.publora.com`) only with your key or connector; Pixfaro
  (`api.pixfaro.com`) only with your key or connector; Anthropic
  (`api.anthropic.com`) only from the optional autopilot with your key.
- **Writes:** your business memory folder, and Publora DRAFTS. No code in
  this bundle publishes immediately, and the autopilot has no scheduling code.
- **Secrets:** read from the environment or `.env` (never committed;
  `scripts/check_no_secrets.py` fails the build if a `.env`, a key-shaped
  string or a memory folder is tracked). Authenticated requests never follow
  redirects, so a key cannot leak to another host.

## Untrusted input

Feed items, reviews, comments and pasted text are data, never instructions
(`references/untrusted-content.md`). They cannot change targets, skip the
compliance check or the approval gate, or make the agent read files or run
commands.

## Dependencies

Runtime code is Python standard library only. `pyyaml` is used by the
maintainer check in CI, not at runtime.
