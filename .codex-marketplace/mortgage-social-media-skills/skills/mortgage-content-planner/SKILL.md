---
name: mortgage-content-planner
description: "Monthly social media content calendar for a mortgage loan officer or mortgage broker: first-run interview (NMLS, states, networks, voice) saved as memory, then a month of posts from rate Thursdays, the FHFA loan-limit release, the home-buying calendar and 100+ post ideas, with network, format and the rule each post needs. Use for: what should I post this month, mortgage content plan. Not for one post (use mortgage-post-writer)."
license: MIT
---

# Mortgage Social Media Skills: content planner

A month of posts for one lending business: what to post, when, on which
network, in which format, and where each idea comes from. The first run is a
short interview that fills the business memory; every later run plans from it.

## When to use

- "content calendar for my lending business", "what should I post this month",
  "plan December", "social media plan for a mortgage loan officer".
- First time with this bundle: it runs the interview first.
- Not for writing a single post (use `mortgage-post-writer`), and not for the
  data-triggered post of the day (use `mortgage-rate-desk`).

## Memory

Memory is the first of these folders that exists: (1) `./mortgage-memory/` in
the current working folder; (2) `memory/` inside this bundle, only when it is a
git clone (`.git` next to it); (3) the plugin setting `memory_dir`, which reads
`${user_config.memory_dir}` here, or the `MORTGAGE_MEMORY_DIR` environment variable,
skipped when empty, still a literal `${...}`, or not an absolute path; (4)
`${CLAUDE_PLUGIN_DATA}/memory`, skipped when literal; (5) no disk: chat mode,
one file in the project, handed back when it changes. Never write under the
plugin's own folder. If nothing exists, offer to create `./mortgage-memory/`
from `memory.example/`. Start every task by printing `memory: <absolute path>`.
Full rules: `../../references/memory.md`.

## Input

- The month (default: next month) and the networks (default: `profile.md`).
- How many posts a week (default: the cadence table below).
- Anything already booked: events, launches, closures, promotions.

## Output

1. One line: `memory: <path>`.
2. A table, one row per post: date (local), network(s), pillar, idea, source
   (feed, calendar date, or the owner's own news), format, card kind or photo.
3. Under it, the three posts that matter most this month, with a first line.
4. The month file `mortgage-memory/plan-YYYY-MM.md` (same table) and new
   ideas appended to `ideas.md` as `proposed`.
5. One closing line: `learned: ...`.

## Steps

1. **Memory.** Resolve the folder and print it. If `profile.md` is still the
   template, run the interview (below) and stop after writing the answers,
   unless the owner also asked for the plan in the same message.
2. **Rules and lessons.** Read `rules.md`, `lessons.md` (candidates are soft
   preferences, promoted rules are hard), `ideas.md` (do not repeat a
   `declined` idea; do not reuse an idea `used` in the last 90 days).
3. **Dated hooks.** From `../../references/calendar.md`, take the month's
   dates that fit this business (state and audience from the profile).
4. **Data hooks.** From `../../references/sources.md`, list which feeds will
   produce posts this month and on which days (the signature post days come
   from `mortgage-rate-desk`; plan the slot, not the numbers). Never put a
   number in the plan that you have not fetched: write "this week's rate", not a
   guessed rate.
5. **Evergreen.** Fill the rest from `../../references/post-ideas.md`, matched
   to the business's pillars and to what the owner said they want more of.
6. **Balance.** Mix pillars across the month (see cadence). No two
   promotional posts in a row. At least one post per week that is pure help.
7. **Compliance pre-check.** For each idea, note the rule it will need
   (`../../references/compliance.md`), so the writer is not surprised: the
   plan names it ("needs the license line", "no client photo without consent").
8. **Write files**, show the table, end with `learned:`.

## The interview (first run only)

One message, numbered, skippable questions:

1. Your name as licensed, your NMLS ID, your company's name and NMLS ID.
2. States you are licensed in; the city and ZIP codes you mostly lend in.
3. Equal Housing Opportunity or Equal Housing Lender (what your company prints; without an answer posts end with "Equal Housing Opportunity").
4. Does your company require compliance approval before you post? (yes/no)
5. Networks you use (Facebook, Instagram, LinkedIn...) and how often you want to post.
6. Who you want to reach: first-time buyers, move-up buyers, veterans, investors, realtor partners.
7. Loan types you want to be known for (conventional, FHA, VA, USDA, jumbo, DSCR...).
8. Paste 2-3 posts or emails you wrote, so drafts sound like you.
9. Words or topics you never want in a post.


Write answers into `profile.md` and `voice.md`; anything skipped stays
`[confirm]`. Say in one line what each missing answer blocks.

## Cadence (default; the owner's choice wins)

| Network | Posts a week | Best for |
|---|---|---|
| Facebook | 3 | buyers, past clients, local |
| Instagram | 2-3 | first-time buyers; the rate card and checklists |
| LinkedIn | 2 | realtor and builder partners, referral sources |
| Threads / X / Bluesky | 1-3 | the Thursday rate line with the source link |


## Pillars

- **Rates and the market** (Thursday Rate Desk, loan limits): the reason to follow you weekly.
- **Education** (how loans work, myths, documents, credit): saves and shares.
- **Local and people** (your city, partners, team, closings with consent): trust.
- **Process and proof** (pre-approval steps, timelines, your own facts from `facts.md`): calls.


## Hard rules

- Plans name sources, not numbers. A number appears only in the writer's post,
  after it was fetched.
- No idea that depends on a client, patient or member story without a line in
  `consent.md`.
- Dates are local to `timezone` in the profile; say the timezone in the table.
- Voice rules: `../../references/voice-rules.md` (no em dashes in any first line).

## Anti-patterns

- A calendar of "national days" that have nothing to do with the business.
- Filling every day: two strong posts beat five filler posts.
- "Post about rates/listings/menu" without saying which source and which day.

## Resources

- `../../references/calendar.md`, `../../references/sources.md`,
  `../../references/post-ideas.md`, `../../references/compliance.md`
- `../../references/memory.md`, `../../references/precedence.md`

## Related skills

- `mortgage-post-writer`: writes, checks and drafts each post of the plan.
- `mortgage-rate-desk`: Thursday Rate Desk, the data-triggered post.

License: MIT.
