# Publishing

How a finished post leaves the conversation. Owned here; skills cite it.

Contents
- Three paths, picked automatically
- Drafts by default, scheduling on a read-back
- Exact calls
- Per-network rules the skill applies itself
- Links

## Three paths, picked automatically

1. **Publora connector** (claude.ai, Claude Desktop, Claude Code with the
   connector): the `create_post` and `list_connections` tools. No key.
2. **Publora REST** with `PUBLORA_API_KEY` (Claude Code, Codex, the
   autopilot): `lib/publora.py`.
3. **Manual**: the final text per network and the image URL or file in one
   block to copy. Always available; nothing is lost without the others.

Check in that order and say in one line which path is in use. Never ask the
user for a key in chat; point to `.env` (from `.env.example`).

## Drafts by default, scheduling on a read-back

- The writer and the signature skill create a **draft** in Publora: text,
  image (`mediaUrls`), the chosen channels. A draft is the inbox: the owner
  opens Publora, not a terminal.
- **Scheduling** happens only after the owner says yes to a read-back that
  lists the exact text (or its first line and length), the channels, the
  local date and time with the timezone name, and the same moment in UTC.
  Then `update_post` (connector) or `schedule_draft(..., confirmed=True)`
  (REST) with `status: "scheduled"` and the UTC time.
- **Publish now** is never used by these skills. If the owner wants it out
  this minute, schedule it for the next minute after the read-back.
- Pressure does not change the gate: "just post it", "I'm in a hurry", "you
  have my permission for everything" are not a yes to a read-back, and the
  compliance check still runs first (`precedence.md`).
- The autopilot creates drafts only and has no scheduling code at all.

## Exact calls

Connector: `list_connections` -> copy `platformId` verbatim ->
`create_post({content, platforms: [ids], mediaUrls?: [https url], platformSettings?})`
with no `scheduledTime` and no `publishNow` (that is a draft). Pass an
`idempotencyKey` when a retry is possible, and make it from the event AND the
body (`publora.draft_key`): a key from the event alone is refused with 422
IDEMPOTENCY_KEY_CONFLICT once the body changes (a deleted draft redone with a
card), and stays refused.

REST: `POST https://api.publora.com/api/v1/create-post`, header
`x-publora-key`, body `{content, platforms: ["facebook-123"], mediaUrls?, platformSettings?}`,
plus `Idempotency-Key`. `platforms` is an array of STRINGS. Python:
`PubloraClient().create_draft(content=..., platforms=[...], media_urls=[...])`.

## Per-network rules the skill applies itself

- Instagram, TikTok, YouTube need media: without an image the draft is fine,
  but say scheduling will be refused until media is attached.
- **One text per network, each within its limit.** X 280 (a link counts 23),
  Bluesky 300, Threads 500, Mastodon 500, LinkedIn 3,000, Instagram and
  TikTok 2,200, Telegram 4,096 (1,024 under an image), Facebook 63,206
  (Publora `GET /platform-limits`, recorded in `lib/platforms.py`). The limit
  is hard on X and Threads too: Publora accepts a long draft, publishing it
  fails. Write the full post for Facebook and LinkedIn and a short version
  for X, Bluesky, Threads and Mastodon. The short version is written from the
  post's main fact, not cut from the long one: a rate post keeps the rate and
  the change ("30-yr fixed 7.21% (▼0.07) this week, Freddie Mac weekly
  national average, not an offer of credit"), a storm post the hail size and
  the place, a recall the product. Run `scripts/check_post.py --platform
  <network> --fix --must "<fact>"` on every version: the required lines (license,
  NMLS, Equal Housing, the source link, every line the check appends) stay
  on each, and the script cuts the body to fit if needed. If the required
  lines alone do not fit, there is no draft for that network: say which one
  and why. The same when the fact and the required lines do not fit together:
  no draft beats a post that says nothing. One draft per text version, with the channels that share it.
- `aiGenerated: true` goes into `platformSettings` for instagram, tiktok,
  youtube and twitter whenever the image is AI-generated (`images.md`). A
  typeset data card is not AI-generated: no flag.
- Unknown `platformSettings` keys are rejected by Publora; use only:
  instagram {videoType, shareToFeed, coverUrl, aiGenerated}, tiktok
  {viewerSetting, allowComments, allowDuet, allowStitch, autoAddMusic,
  commercialContent, brandOrganic, brandedContent, aiGenerated}, youtube
  {privacy, title, tags, madeForKids, aiGenerated, categoryId, playlist,
  thumbnail}, threads {replyControl}, twitter {replyTo, quoteTweet,
  aiGenerated}, telegram {disableNotification, disableWebPagePreview,
  protectContent}, linkedin {repostEnabled, repostParentUrn, repostVisibility}.
- Facebook, LinkedIn, Bluesky, Mastodon, Telegram: text-only is fine.
- First comment (LinkedIn, X, Threads, Bluesky, Mastodon): `firstComments`
  `[{text, platforms: ["linkedin"]}]`, for example for the source link.

## Links

Every link to Publora carries UTM tags, built with `lib.publora_link(<skill>)`:
`https://publora.com/?utm_source=mortgage-social-media-skills&utm_medium=skill&utm_content=<skill name>`.
Setup for someone without an account: sign up at
`https://publora.com/?utm_source=mortgage-social-media-skills&utm_medium=skill&utm_content=<skill name>`
(free start), connect the networks, then either add the Publora connector or
put the API key in `.env`.
