# Images

What picture goes with a post, and how it is made. Owned here; skills cite it.

Contents
- The default: a data card
- Card kinds
- How a card is made
- AI images: only where allowed, always labeled
- Your own photos
- Images (optional) setup

## The default: a data card

Most posts in this bundle carry a number, a date, a short list or an event.
The picture for them is a **typeset card** showing exactly that: the rate and
its change, the hail size and the town, three things to check, the service
time. Typeset means the text is set like a document, not drawn by a model, so
the number on the card is the number from the source, letter for letter.

## Card kinds

| Kind | Shows | Spec |
|---|---|---|
| stat | one figure and its label, source line | `{"kind": "stat", "value": "...", "label": "...", "source": "..."}` |
| table | 2-6 rows | `{"kind": "table", "title": "...", "header": [...], "rows": [[...]], "source": "..."}` |
| checklist | 3-5 short items | `{"kind": "checklist", "title": "...", "items": [...]}` |
| event | what, when, where, call to action | `{"kind": "event", "title": "...", "when": "...", "where": "...", "cta": "..."}` |
| quote | one sentence and who said it | `{"kind": "quote", "quote": "...", "name": "..."}` |

Every value on a card must already be in the post's source data or memory:
the same number check as the text (`lib/provenance.py`).

## How a card is made

With a Pixfaro key (`PIXFARO_KEY`) or the Pixfaro connector:

1. Read the live template list (`GET https://api.pixfaro.com/v1/templates`,
   public, free, or the connector's `list_templates`).
2. Use the template for the kind: `stat-card` (value, label, the change as
   `delta` like "▲ 0.17 from last week", one `context` line, the source),
   `table-card`, `checklist-card` (the source as its footer), `event-card`
   (date, place, call to action), `quote-card`. The business name goes under
   the card. `lib/cards.py` fills the slots: `cards.render(spec,
   business_name=...)`. Only if a template is missing from the catalog (an
   older account) does it fall back to `quote-card` for a stat and
   `post-card` for the rest, still typeset.
3. Text past a slot's maximum is refused by Pixfaro, not cut: shorten first.
4. The result is a hosted https URL. It goes straight into the Publora draft
   as `mediaUrls`; the owner sees one draft with the picture on it.
5. A card costs about $0.02. Say so the first time in a session.

Brand: when `brand.md` has `pixfaro_brand_kit: yes`, cards use `style: "brand"`
(the saved palette). The first time, with a full-scope key and the owner's
yes, `PUT /v1/brand-kit/identity` with the business name and palette, then set
`pixfaro_brand_kit: yes`.

## AI images: only where allowed, always labeled

A model-generated image is allowed only where `compliance.md` of this bundle
says so (typically an abstract seasonal illustration or an article cover).
Never for anything the viewer would take as a real photo of the business's
work, place, product, client, patient, animal or property. When one is used:

- model `nano-banana-2` via `POST /v1/images/generations`, no text in the image;
- `aiGenerated: true` in `platformSettings` for every instagram, tiktok,
  youtube and twitter target (`publishing.md`);
- say "AI-generated illustration" to the owner in the read-back.

## Your own photos

The owner's photos are always better than any card for work, place and
people. A photo that shows a client, patient, member, child, pet with its
owner, or a home address needs an entry in `consent.md` first (`memory.md`).
The skill asks for a public https URL or uploads through Publora's media flow.

## Images (optional) setup

Images are optional; every skill works without them (text-only draft, or the
owner's own photo). For cards: a Pixfaro account (pixfaro.com, $1 free credit
on sign-up), then either the Pixfaro connector or `PIXFARO_KEY=pf_live_...` in
`.env`.
