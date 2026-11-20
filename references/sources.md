# Sources of mortgage post ideas

Where posts come from, how often, in what format, and what to do when a
site refuses a script. Checked 2026-11-19 from a US server unless noted.

Contents
- Freddie Mac PMMS (weekly, automatic)
- FHFA conforming loan limits (yearly)
- FHA loan limits (yearly)
- CFPB newsroom (as published)
- Federal Reserve FOMC calendar (8 a year)
- Housing market data you can quote
- Your own sources
- Manual fallback for any source

## Freddie Mac PMMS (weekly, automatic)

- **What:** Primary Mortgage Market Survey, average 30-year and 15-year fixed
  rates, published Thursdays at 12:00 ET (Wednesday in a holiday week).
- **URL:** `https://www.freddiemac.com/pmms/docs/PMMS_history.csv`
  (full history CSV, free, no key; HTTP 200 on 2026-11-19). Page:
  `https://www.freddiemac.com/pmms`.
- **Format:** `date,pmms30,pmms30p,pmms15,pmms15p,...`, date as M/D/YYYY.
  Latest row on 2026-11-19: 11/19/2026, 30-year 7.28, 15-year 6.66; the week
  before: 7.11 and 6.45.
- **Parser:** `lib/feeds/pmms.py` (`parse`, `latest`): this week, last week,
  change, the same week a year ago, all as the strings the CSV holds.
- **Used by:** `mortgage-rate-desk` and the autopilot (Thursdays and Fridays
  17:30 UTC).
- **Say it right:** "the average 30-year fixed rate in Freddie Mac's weekly
  survey", never "today's rate" or "my rate".

## FHFA conforming loan limits (yearly)

- **What:** the next year's baseline and high-cost-area limits for
  conforming loans, by county.
- **When:** late November (11/25/2025, 11/26/2024, 11/28/2023,
  11/29/2022). The 2027 values were not out on 2026-11-19.
- **URL:** `https://www.fhfa.gov/data/conforming-loan-limit` (HTTP 200;
  county XLSX and CSV links on the page).
- **Post:** "2027 conforming loan limit for <county>" the day it is
  published: quote the county row exactly. Manual: the owner pastes the row or
  the skill reads the CSV the owner downloaded.

## FHA loan limits (yearly)

- HUD publishes FHA limits for the next year shortly after FHFA (mortgagee
  letter). URL and format not verified by script; manual paste of the county
  row.

## CFPB newsroom (as published)

- `https://www.consumerfinance.gov/about-us/newsroom/feed/` (RSS, HTTP 200).
  Consumer-facing news worth explaining (closing cost rules, credit reporting
  changes). Parser: `lib/feeds/rss.py`. Quote the headline, link it, explain
  in plain words; never predict enforcement.

## Federal Reserve FOMC calendar (8 a year)

- Meeting dates: `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`
  (HTML; not parsed). The evergreen post: "The Fed doesn't set mortgage
  rates" on the day after a meeting, with no rate prediction.

## Housing market data you can quote

- realtor.com monthly ZIP and metro inventory CSVs (median list price,
  days on market): `https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Zip.csv`
  (HTTP 200, ~7 MB). Good for a local "what buyers are seeing" post with a
  realtor partner.
- Census new residential construction API (`https://api.census.gov/data/timeseries/eits/resconst`).

## Your own sources

- Closings (only with a `consent.md` entry; no address, no loan figures).
- Pre-approval milestones, first-time buyer classes, realtor partner events.
- Questions clients asked this week (anonymized): the best education posts.
- Your facts in `facts.md` (years in business, languages spoken, programs).

## Manual fallback for any source

If a site refuses scripts or the feed changes shape:
1. Open the page in a browser.
2. Copy the row or table you need and paste it into the chat, or save the CSV
   and give the path.
3. The skill parses what you pasted and quotes it exactly, with the date you
   say it was published. Nothing is filled in from memory.
