# Autopilot

Posts at the moment of the event, while you are not at the keyboard. The
autopilot watches this bundle's source on a schedule and leaves a **draft** in
Publora; you open Publora, read it, and schedule it or delete it.

Contents
- What it does and never does
- Set up (10 minutes, your own copy on GitHub)
- Without a model key
- Claude Code instead of GitHub
- Limits and costs
- Troubleshooting

## What it does and never does

Does: on its cron (`.github/workflows/autopilot.yml`), runs
`autopilot/watch.py`, which asks `autopilot/trigger.py` whether the source has
a new event for your area (a new weekly Freddie Mac PMMS rate, published Thursdays at noon Eastern). For each new event it writes
the post (with Claude, or from `autopilot/templates.json`), runs the same
compliance check and number check as the skills, adds a data card when a
Pixfaro key is set, fits the text to each network (a short version for X,
Bluesky, Threads and Mastodon, the full one for Facebook and LinkedIn, every
required line kept on each; a network where they cannot fit is skipped and
the summary says why), and creates one draft per text version in Publora,
with an idempotency key made from the event and the request body.

Never: publishes or schedules (there is no code path for it); drafts the
same event twice (event ids are kept in `autopilot/state.json`); drafts more
than `max_drafts_per_day` events (default 3, hard cap 10); drafts a text that fails
the check (the reason goes to the run's summary instead).

## Set up (10 minutes, your own copy on GitHub)

1. Make your own copy: on this repo's page, **Use this template**, **Create
   a new repository**, and choose **Private**. A fork works too, but a fork
   of a public repo is always public, and so are the files you commit to it:
   the config in step 2 (business name, license or NMLS line, service area)
   and `autopilot/state.json`, which the workflow commits back after each
   draft.
2. Copy `autopilot/config.example.json` to `autopilot/config.json` and fill
   it: business name, the license or ID line, state, the area fields, your
   Publora channel ids (`platforms`, from Publora's channel list, for example
   `"facebook-1234567890"`), language. Commit it. It holds no secret, but it
   is public in a public copy.
3. In your copy: Settings, Secrets and variables, Actions, add
   `PUBLORA_API_KEY` (required), `ANTHROPIC_API_KEY` (optional),
   `PIXFARO_KEY` (optional).
4. Actions tab: enable workflows, open "Autopilot", "Run workflow" once with
   `dry_run: true` and read the summary.
5. Leave it on. The schedule is in the workflow file (`cron`, UTC).

## Without a model key

No `ANTHROPIC_API_KEY`, or `"mode": "no-llm"` in the config, or
`python3 autopilot/watch.py --no-llm`: the post is built from
`autopilot/templates.json` with the event's data filled in. Plainer, still
checked, still a draft.

## Claude Code instead of GitHub

`/loop 1h use mortgage-rate-desk for my area and leave drafts in Publora`, or a
scheduled routine with the same prompt. Same skill, same checks.

## Limits and costs

A run reads one or two public feeds and, on an event, one model call (a few
cents) and one card ($0.02). GitHub Actions minutes for a public copy are free;
a private copy uses the account's included minutes (a run takes under a
minute). Publora drafts count toward nothing until scheduled.

## GitHub limits to know

- **Scheduled workflows stop after 60 days without activity** in a public
  repo. The autopilot commits `autopilot/state.json` only when it drafts, so a
  quiet season can switch it off silently. Once a month, open the Actions tab
  (GitHub shows a banner to re-enable it) or push any small commit.
- **Minutes:** a public fork runs free. A private copy bills each run as at
  least one minute: a 30-minute schedule is about 1,440 minutes a month,
  against 2,000 free minutes on GitHub Free. Use a slower cron if you share
  those minutes with other work.

## Troubleshooting

| Summary line | Meaning |
|---|---|
| `Source check failed` | the feed is down or changed; nothing was drafted. The manual path in `sources.md` still works |
| `NOT drafted, check FAIL` | the text broke a rule that could not be fixed automatically, often a missing license or ID in the config |
| `PUBLORA_API_KEY is not set` | add the secret; the run fell back to a dry run |
| `Daily limit ... reached` | raise `max_drafts_per_day` (max 10) or wait. The limit counts events; one event can make a draft per text version (say one for X and Bluesky, one for Facebook and LinkedIn) |
| `not drafted for twitter-...: the opening line and the required lines need N characters` | the lines the rules require do not fit that network; the other networks got their draft. Post there by hand or take the channel out of `platforms` |
