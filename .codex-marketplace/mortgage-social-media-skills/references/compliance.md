# Compliance for mortgage loan officer posts

What the writer and the Rate Desk check on every post, with the source, an
example and the fix. Machine half: `compliance-rules.json` (same ids), run by
`scripts/check_post.py` and the autopilot. Rules every vertical shares:
`compliance-common.md`.

Verified 2026-11-19 against the sources named; reviewed quarterly. **Not
legal advice.** Many lenders require compliance approval before any post
(`compliance_review: yes` in the profile): then a draft in Publora is where the
post waits for that approval, and the skills say so.

Contents
- How to read a finding
- Reg Z: trigger terms and APR
- Rates from a survey
- NMLS ID and the Equal Housing line
- Misleading claims (Reg N / MAP Rule)
- RESPA and realtor co-marketing
- Fair lending wording
- Testimonials and reviews
- States
- Images
- What the check does not cover

## How to read a finding

| Level | Meaning | What the writer does |
|---|---|---|
| block | the post cannot go out as written | rewrites the passage, says what changed |
| fix | a required element is missing | adds it from the profile (NMLS line, Equal Housing, approved APR example); if the profile lacks it, asks, never invents |
| flag | a person must decide | keeps it, shows it, the owner decides |

## Reg Z: trigger terms and APR

Regulation Z §1026.24 governs any advertisement for closed-end credit, and a
loan officer's social post is advertising.

| Id | Level | Rule | Fails | Passes |
|---|---|---|---|---|
| REGZ-PAYMENT-TRIGGER | fix | A payment amount is a trigger term: the post must also state the down payment, the repayment terms and the APR (1026.24(d)) | "Own this home for $1,200/mo!" | "Ask me what your payment could look like; I'll run the real numbers with you." |
| REGZ-DOWNPAYMENT-TRIGGER | fix | A down payment amount or percent, including 0% or "no money down", is a trigger term (1026.24(d)(1)(i)) | "Buy with 3% down!" | "Low down payment options exist. Let's see which fit you." |
| REGZ-TERM-OFFER | fix | Offering a number of payments or a term ("get a 15-year loan", "360 payments") is a trigger term (1026.24(d)(1)(ii)) | "Lock a 15-year loan today" | "15-year vs 30-year: what changes besides the payment" (education, no offer) |
| REGZ-RATE-OFFER-APR | fix | A rate you offer must be stated as an APR (1026.24(c)) | "Rates as low as 6.25%!" | no own rate; or the full approved APR example |

The writer's default fix is to **remove the trigger term**: the post becomes
education and a call to talk. Adding the disclosure is the alternative only
when the profile has `apr_disclosure`, an example your compliance team
approved, written to include the APR, the down payment and the terms (for
example: "Example: $400,000 purchase, 20% down, 30-year fixed, 360 payments,
rate 6.875%, APR 7.012% as of <date>; your terms will vary." with your own
approved figures). The skills never compute or invent an APR.

## Rates from a survey

| Id | Level | Rule |
|---|---|---|
| RATE-AVERAGE-LABEL | fix | A percent rate in the post (from Freddie Mac PMMS) carries the source and a line that it is a weekly national average and not a quote or an offer |

Reporting "the 30-year fixed averaged 7.28% this week (Freddie Mac PMMS)" is
market news, not an offer of your loan; the label keeps it from being read as
one. The appended line: "Rates shown are Freddie Mac PMMS weekly national
averages, not a quote or an offer of credit. Your own rate depends on your
situation." It deliberately contains no "APR": an APR counts only with its
figure, so the label can never satisfy the APR rule for an offer. Never round the survey rate, never call it "my rate".

## NMLS ID and the Equal Housing line

| Id | Level | Rule |
|---|---|---|
| NMLS-ID | fix | Every post carries the loan officer's name and NMLS ID and the company's name and NMLS ID |
| EQUAL-HOUSING | fix | Every post carries the Equal Housing statement the company uses |

NMLS: state rules require the originator's unique identifier on advertising;
Texas spells it out for social media (Texas SML, "RMLO Social Media
Requirements and Best Practices", 2025); Maryland accepts the ID on the
profile instead of each post (COMAR 09.03.06.06). The bundle adds the line to
every post as the safe default. Line format, from the profile:
`<owner_name> | NMLS #<nmls_id> | <company_name> | NMLS #<company_nmls_id>`.

Equal Housing: a legal requirement for some lenders (FDIC-supervised banks
use "Equal Housing Lender", 12 CFR 338.3) and the policy of most others. As a
federal rule for every non-bank originator it is **not verified**; the bundle
adds it by default and the owner may remove it on their compliance team's
written instruction.

## Misleading claims (Reg N / MAP Rule)

The Mortgage Acts and Practices Advertising Rule (Regulation N, 12 CFR 1014)
bars misrepresenting the terms of mortgage credit.

| Id | Level | Rule | Fails |
|---|---|---|---|
| MAP-GUARANTEE | block | No guaranteed approval, "everyone qualifies", "no credit check", "100% approval" | "We guarantee your approval!" |
| MAP-GOVERNMENT | flag | No implied government affiliation or official program | "New government program pays your down payment" |
| MAP-FORECAST | flag | No rate forecast stated as fact | "Rates will drop next month, buy now" |
| MAP-FIXED | flag | "Fixed" next to an adjustable product needs the period | "5/6 ARM, fixed for life" |
| SUPERLATIVE-UNPROVEN | flag | "Lowest rates in town", "#1 lender" need proof shown in the post | "Best rates in Austin" |

FHA, VA and USDA loans are government-insured or guaranteed; saying so is
fine. Implying that you are the government, or that a program is free money
for everyone, is not.

## RESPA and realtor co-marketing

| Id | Level | Rule |
|---|---|---|
| RESPA-REFERRAL | flag | Co-marketing must not look like paying or being paid for referrals |

RESPA §8 (12 U.S.C. 2607) and Regulation X (12 CFR 1024.14) prohibit
anything of value for referrals of settlement business. A joint post with a
realtor is fine when each pays its fair share of real costs (CFPB Compliance
Bulletin 2015-05 on marketing services agreements). The skill flags wording
like "referral fee", "send me your buyers and I'll cover your ads".

## Fair lending wording

| Id | Level | Rule |
|---|---|---|
| FAIR-LENDING-WORDS | flag | No wording that targets or excludes by familial status, age proxies, religion, national origin, race, sex or disability |

ECOA / Regulation B (12 CFR 1002.4(b)) bars statements that would discourage
applicants on a prohibited basis; the Fair Housing Act (42 U.S.C. 3604(c))
covers housing-related advertising. "Perfect for young families" is flagged;
"Down payment help programs in Travis County" is fine. When suggesting a paid
boost, never suggest audience targeting by age, family status, ZIP as a proxy
for race, or religion.

## Testimonials and reviews

Common rules apply (FTC Consumer Reviews Rule, Endorsement Guides). For a
lender also: a client's closing story or photo needs a `consent.md` entry and
must not show loan terms, an address or a credit detail. Results in a
testimonial ("closed in 12 days") must be typical or the post says what is
typical.

## States

| State | What changes | Source |
|---|---|---|
| TX | Social media: name and NMLS ID on the profile and on ads; the company's NMLS ID; see the SML guide for page names and posts | Texas SML RMLO social media requirements (2025) |
| MD | NMLS ID may sit on the profile rather than each post | COMAR 09.03.06.06 |
| All others | the bundle's default (NMLS line on every post) | state SAFE Act rules (vary; not verified one by one) |

## Images

- The rate card shows the survey numbers only, with "Freddie Mac PMMS, week
  of <date>" and no APR of your own.
- No AI image of a house that looks like a real listing, no AI "client".
- A closing photo needs a `consent.md` entry; no address, no loan figures.

## What the check does not cover

Company-specific rules (your compliance team's approved language), investor
overlays, and state rules beyond the table. When `compliance_review: yes`,
every draft says "awaiting compliance approval" in the read-back.
