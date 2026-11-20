# Mortgage Social Media Skills for Claude and Codex

<p align="center">
  <img src="https://img.shields.io/github/v/release/sergebulaev/mortgage-social-media-skills?color=0F766E&label=release" alt="Latest release">
  <img src="https://img.shields.io/badge/Claude_Code-Compatible-D97757?logo=anthropic&logoColor=white" alt="Claude Code Compatible">
  <img src="https://img.shields.io/badge/Codex-Compatible-111827" alt="Codex Compatible">
  <img src="https://img.shields.io/badge/Claude-Skills-8A63D2" alt="Claude Skills">
  <img src="https://img.shields.io/badge/License-MIT-22C55E.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/PRs-welcome-F59E0B.svg" alt="PRs Welcome">
</p>

**Claude skills for mortgage loan officer social media.** Three skills for
loan officers and mortgage brokers: a **monthly content calendar**, a
**post writer that checks Reg Z** (trigger terms and APR), your **NMLS ID**
and the **Equal Housing** line on every post, and the **Thursday Rate Desk**:
every Thursday Freddie Mac publishes its weekly mortgage rate survey, and the
skill turns it into a rate post, a LinkedIn version for your realtor
partners and a rate card, with every number taken from the survey. Posts
land as drafts in [Publora](https://publora.com/?utm_source=mortgage-social-media-skills&utm_medium=skill&utm_content=readme)
for Facebook, Instagram, LinkedIn, Threads, X and more. Mortgage social
media post ideas included: 100+ of them.


## What you can do

- "Write this week's rate post" -> this week's 30-year and 15-year averages
  from Freddie Mac, the change from last week and a year ago, a rate card,
  your NMLS and Equal Housing lines, drafts in Publora.
- "Check this post: Own this home for just $1,200/mo!" -> FAIL: a payment
  amount is a Reg Z trigger term; the fix drops it or adds your approved APR
  example; NMLS ID added.
- "Plan December" -> holiday closings, year-end tax documents, the FHFA
  2027 loan-limit post, four rate Thursdays, education and partner posts.
- "Turn my notes on FHA vs conventional into an Instagram carousel" ->
  slides, caption, check, draft.


## The 3 skills

| Skill | What it does | Say |
|---|---|---|
| `mortgage-content-planner` | First run: a short interview about your lending business (saved as memory). Then a month plan: dated hooks, data posts, evergreen ideas, network and format per post | "Plan my posts for next month" |
| `mortgage-post-writer` | A post per network in your voice, the Reg Z and NMLS check with every fix shown, a data card or your photo, a draft in Publora | "Write a post for first-time buyers about down payment help" |
| `mortgage-rate-desk` | **Thursday Rate Desk.** Every Thursday Freddie Mac publishes the weekly mortgage rate survey. The skill reads it, compares it with last week and last year, and drafts a rate post, a partner version for LinkedIn and a rate card, each passing the Reg Z, NMLS and Equal Housing check. | "Write this week's rate post" |

## Start in Claude Desktop (no coding)

1. Make a folder for your lending business's social media, for example `Social`.
2. In Claude Desktop open **Customize**, **Plugins**, **Add**, **Add
   marketplace**, **Add from a repository**, paste
   `sergebulaev/mortgage-social-media-skills` and install the plugin.
3. Optional: connect the **Publora** connector (drafts and scheduling) and
   the **Pixfaro** connector (data cards) under Customize, Connectors.
4. Start a session in your `Social` folder and say: **"Plan my posts for next month"**.

## Other ways to install

**Claude Code**

```
/plugin marketplace add sergebulaev/mortgage-social-media-skills
/plugin install mortgage-social-media-skills@mortgage-social-media-skills
```

**Codex CLI**

```bash
codex plugin marketplace add sergebulaev/mortgage-social-media-skills
codex plugin add mortgage-social-media-skills@mortgage-social-media-skills
```

**claude.ai (web)**: Customize, Plugins, Add marketplace,
`sergebulaev/mortgage-social-media-skills`.

**Any agent that reads SKILL.md (OpenClaw and others)**

```bash
npx skills add sergebulaev/mortgage-social-media-skills
```

## What it needs

| You have | What works |
|---|---|
| Nothing but Claude or Codex | memory, monthly plans, posts with the compliance check, the signature skill with data you paste; you copy the final text |
| A Publora account ([free Starter plan](https://publora.com/pricing?utm_source=mortgage-social-media-skills&utm_medium=skill&utm_content=readme): 3 accounts, 15 posts a month; Pro for more) | drafts land in Publora with the picture attached; scheduling after your yes; the autopilot |
| Optional: a Pixfaro key or connector ($1 free credit) | data cards for posts (about $0.02 each) |
| Optional: an Anthropic API key | the autopilot writes with Claude instead of templates |

Publora plans on [publora.com/pricing](https://publora.com/pricing?utm_source=mortgage-social-media-skills&utm_medium=skill&utm_content=readme) (read
2026-11-19): Starter free forever (3 social accounts, 15 posts a month, 3
scheduled at a time up to 7 days ahead, all networks except X); Pro from $5.99
per account a month.

## Rules it checks

- Reg Z advertising rules (12 CFR 1026.24): trigger terms, APR with any rate offer.
- NMLS ID of the loan officer and the company; the Equal Housing line.
- Reg N / MAP Rule (12 CFR 1014): no guaranteed approval, no implied government affiliation.
- RESPA §8 for realtor co-marketing; fair lending wording.
- FTC reviews and endorsements rules for testimonials; no invented numbers.


The rules are the bundle's reading of public sources, each with its source
and the date it was checked (`references/compliance.md`, verified
2026-11-19, reviewed quarterly). **Not legal advice; you are responsible
for your posts.**

## Autopilot: posts while you work

`.github/workflows/autopilot.yml` watches the Freddie Mac weekly mortgage rate survey (PMMS) on a schedule
and leaves **drafts** in Publora, never live posts. Fork, add
`autopilot/config.json` and the `PUBLORA_API_KEY` secret, done. Details:
`references/autopilot.md`. No model key? It writes from templates (`--no-llm`).

## Memory

Your business lives in `./mortgage-memory/` in your working folder:
profile (city, ZIPs, state, NMLS IDs, licensed states, the Equal Housing line), voice, rules, facts,
ideas, lessons, consent. Plain markdown. Keep it private.

## Where the ideas come from

- **Freddie Mac PMMS**, weekly on Thursday (the Rate Desk, automatic).
- **FHFA conforming loan limits**, every late November for the next year.
- **CFPB newsroom**, Fed meeting dates, the home-buying season calendar.
- Your own: closings (with consent), pre-approval milestones, partner events.


Full list with URLs, schedules and the manual fallback: `references/sources.md`.
100+ post ideas: `references/post-ideas.md`. Year calendar: `references/calendar.md`.

<details>
<summary>For developers</summary>

- Runtime is Python standard library only. `lib/` holds the compliance lint
  (`lib/compliance.py` + `references/compliance-rules.json`), the number check
  (`lib/provenance.py`), feed parsers (`lib/feeds/`), Publora and Pixfaro
  clients, memory helpers.
- `python3 scripts/check_post.py post.txt --memory ./mortgage-memory --source data.json --fix`
- `python3 -m unittest discover -s tests` (offline), `python3 evals/run_evals.py --list`
  (behaviour evals against a fake Publora, needs the `claude` CLI).
- Part of a family of vertical social media skill bundles sharing one core;
  shared files are listed in `.vertical-core.json`.

</details>

---

Built by Serge Bulaev, founder of Publora. MIT License.
