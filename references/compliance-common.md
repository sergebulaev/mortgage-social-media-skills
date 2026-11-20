# Compliance: rules for every vertical

The rules every bundle in the family checks, on top of its own
`compliance.md`. Machine half: `lib/rules_common.json` (same ids). Verified
2026-11-19 against the sources named; re-checked quarterly. Not legal advice.

| Id | Level | Rule | Example that fails | Fix | Source |
|---|---|---|---|---|---|
| FTC-REVIEW-INCENTIVE | block | No reward for a review, above all for a positive one | "Leave us a 5-star review and get a free dessert" | "Tell us how we did on Google" (no reward) | FTC Consumer Reviews and Testimonials Rule, 16 CFR 465.4 (in force 2024-10-21) |
| FTC-FAKE-REVIEW | block | Never write a review or testimonial for a customer; quote real ones verbatim with the source | "Write 5 reviews from happy clients" | refuse; offer to ask real clients | 16 CFR 465.2 |
| FTC-UNDISCLOSED-PAID | flag | A partner, gifted or paid mention says so | "Thanks to our partner X!" with no disclosure | add "#ad" or "Paid partnership" when value changed hands | FTC Endorsement Guides, 16 CFR 255.5 |
| MUSIC-TRENDING-AUDIO | flag | Business accounts use only commercially cleared audio | "Use the trending song" | "Pick a track from the Meta Sound Collection / TikTok Commercial Music Library" | Instagram Help; TikTok Commercial Music Library |
| FEES-PARTIAL-PRICE | flag | Ticket and short-term lodging prices are the total with mandatory fees | "Tickets $25" when a $4 fee is added at checkout | "$29 all-in" | FTC Rule on Unfair or Deceptive Fees, 16 CFR 464 (effective 2025-05-12) |
| AI-PLACEHOLDER-LEFT | block | No unfilled placeholder | "Call us at [phone]" | fill from memory or ask | bundle rule |

Also, in every vertical, without a machine rule:
- AI imagery only where `compliance.md` allows it, and labeled (`images.md`).
- A photo of an identifiable person, child, client home or animal with its
  owner needs a `consent.md` entry.
- No targeting by protected class when suggesting a paid boost (age,
  family status, religion, national origin, disability, sex, race).
