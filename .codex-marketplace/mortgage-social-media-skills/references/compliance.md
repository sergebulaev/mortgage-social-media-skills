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
| REGZ-TERM-OFFER | fix | A term or number of payments is a trigger term; the commentary's own example is "30-year mortgage" (1026.24(d)(1)(ii), comment 24(d)(1)-2) | "Ask me about a 30-year mortgage", "360 payments" | "15-year vs 30-year fixed: what changes besides the payment" (education, see the note below) |
| REGZ-FINANCE-CHARGE | fix | The amount of a finance charge (points, a fee figure) is a trigger term (1026.24(d)(1)(iv)) | "Only 1 point!" | "Ask me how points work" |
| REGZ-RATE-OFFER-APR | fix | A rate you offer must be stated as an APR (1026.24(c)) | "Rates as low as 6.25%!" | no own rate; or the full approved APR example |
| REGZ-DOWNPAYMENT-TRIGGER | flag | A down payment percent or amount ("3% down"). House policy, see below | "Buy with 3% down!" | "Low down payment options exist. Let's see which fit you." |
| REGZ-COUNSELOR | block | No "counselor" for a for-profit mortgage advertiser (1026.24(i)(6)) | "Talk to your mortgage counselor" | "Talk to your loan officer" |

**Down payment, honestly.** The official commentary limits the down payment
trigger to credit sales and says "no downpayment" is not a trigger term
(comment 24(d)(1)-1). A mortgage is usually not a credit sale. Many lenders'
compliance teams still treat "3% down" in a loan ad as a trigger, so the
bundle FLAGS it for your decision instead of failing it, and does not flag
"zero down" or "no money down".

**Survey rates are the bundle's interpretation.** The Rate Desk treats the
Freddie Mac PMMS average, labeled as an average and not an offer, as market
news rather than an advertisement of your credit terms. That is this bundle's
reading, not settled law: confirm it once with your compliance team.

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
| RATE-AVERAGE-LABEL | fix | A post that quotes a Freddie Mac / PMMS / survey rate carries a line that it is a weekly national average and not a quote or an offer. It is not applied to a post that states your own APR (the offer rules apply then) (12 CFR 1014.3(b)) |

Reporting "the 30-year fixed averaged 7.28% this week (Freddie Mac PMMS)" is
market news, not an offer of your loan; the label keeps it from being read as
one. The appended line: "Rates shown are Freddie Mac PMMS weekly national
averages, not a quote or an offer of credit. Your own rate depends on your
situation." It deliberately contains no "APR": an APR counts only with its
figure, so the label can never satisfy the APR rule for an offer. Never round the survey rate, never call it "my rate".

## NMLS ID and the Equal Housing line

| Id | Level | Rule |
|---|---|---|
| NMLS-ID | fix | Every post carries the loan officer's name and NMLS ID and the company's name and NMLS ID (the check needs both numbers) |
| EQUAL-HOUSING | fix | Every post carries the Equal Housing line: `eho_statement` from the profile ("Equal Housing Lender" for a lender that prints it), or "Equal Housing Opportunity" when it is empty. Not required when the profile says `equal_housing_line: off` |

NMLS: state rules require the originator's unique identifier on advertising;
Texas spells it out for social media (Texas SML, "RMLO Social Media
Requirements and Best Practices", 2025); Maryland accepts the ID on the
profile instead of each post (COMAR 09.03.06.06). The bundle adds the line to
every post as the safe default. Line format, from the profile:
`<owner_name> | NMLS #<nmls_id> | <company_name> | NMLS #<company_nmls_id>`.

Equal Housing: a legal requirement for some lenders (FDIC-supervised banks
use "Equal Housing Lender", 12 CFR 338.3) and the policy of most others. As a
federal rule for every non-bank originator it is **not verified** (federal
credit unions: 12 CFR 701.31); the bundle adds it by default (maintainer's decision
of 2026-11-23), even when the profile has no `eho_statement`: then the line
reads "Equal Housing Opportunity". A lender that prints "Equal Housing
Lender" puts that in `eho_statement`. To switch the line off, add
`- equal_housing_line: off` to `profile.md` (also accepted: no, false, none),
only on your compliance team's written instruction.

## Misleading claims (Reg N / MAP Rule)

The Mortgage Acts and Practices Advertising Rule (Regulation N, 12 CFR 1014)
bars misrepresenting the terms of mortgage credit.

| Id | Level | Rule | Fails |
|---|---|---|---|
| MAP-GUARANTEE | block | No guaranteed approval or closing, "everyone qualifies", "no credit check", "100% approval" | "Pre-approved in 24 hours, guaranteed." |
| MAP-GOVERNMENT | flag | No implied government affiliation or official program (1014.3(n); Reg Z 1026.24(i)(3)) | "The government wants you to own a home" |
| MAP-FORECAST | flag | No rate forecast stated as fact (1014.3(b)) | "Rates will probably drop next month, buy now" |
| MAP-FIXED | flag | "Fixed" for an adjustable product needs the period (1014.3(g); Reg Z 1026.24(i)(1)) | "5/6 ARM, fixed for life" |
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
realtor is fine when each pays its own share of the cost at market value:
a payment must be for goods or services actually furnished, not for the
referral (12 CFR 1024.14(g)(1)(iv), (g)(2); CFPB RESPA Section 8 FAQs,
October 7, 2020, which replaced Compliance Bulletin 2015-05 on marketing
services agreements, rescinded the same day). The skill flags wording
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
overlays, state rules beyond the table, reverse-mortgage advertising (HUD and
state rules for HECM ads are not checked), HELOC/open-end credit ads (12 CFR
1026.16), and whether your approved APR example matches the terms a post
advertises (the check only sees that one is there). When `compliance_review: yes`,
every draft says "awaiting compliance approval" in the read-back.
