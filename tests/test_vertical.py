"""Mortgage vertical tests: compliance graders, the PMMS parser, the trigger.

Deterministic graders for the cases the design names (VERTICALS-SPEC §14):
a loan officer post with "$1,200/mo" and no APR must FAIL.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import compliance, memory, provenance  # noqa: E402
from lib.feeds import pmms  # noqa: E402

FIX = ROOT / "tests" / "fixtures"
PROFILE = memory.load_profile(FIX / "memory")


def ids(report):
    return {f.rule_id for f in report.findings}


class RegZ(unittest.TestCase):
    def test_payment_without_apr_fails(self):
        rep = compliance.autofix("Own this South Austin home for just $1,200/mo! Call Dana.", profile=PROFILE)
        self.assertEqual(rep.verdict, "FAIL")
        self.assertIn("REGZ-PAYMENT-TRIGGER", ids(rep))

    def test_payment_with_full_disclosure_passes_trigger(self):
        text = ("Payments of $2,661 a month. Example: $400,000 purchase, 20% down payment, 30-year fixed, "
                "360 payments, rate 6.875%, APR 7.012% as of 11/19/2026. Not an offer of credit.")
        rep = compliance.check(text, profile=PROFILE)
        self.assertNotIn("REGZ-PAYMENT-TRIGGER", ids(rep))

    def test_percent_down_flagged_zero_down_not(self):
        # Reg Z comment 24(d)(1)-1: "no downpayment" is not a trigger term.
        for t in ("Buy with 3% down this spring", "3.5 percent down options"):
            self.assertIn("REGZ-DOWNPAYMENT-TRIGGER", ids(compliance.check(t, profile=PROFILE)), t)
        for t in ("VA buyers: $0 down!", "No money down options!", "Zero down VA loans for veterans"):
            self.assertNotIn("REGZ-DOWNPAYMENT-TRIGGER", ids(compliance.check(t, profile=PROFILE)), t)

    def test_term_and_points_triggers(self):
        for t in ("Ask me about a 30-year mortgage", "Pay off your mortgage in 15 years", "Only 1 point to the borrower"):
            rep = compliance.autofix(t, profile=PROFILE)
            self.assertEqual(rep.verdict, "FAIL", t)

    def test_approved_apr_example_reaches_pass(self):
        prof = dict(PROFILE, apr_disclosure=(
            "Example: $400,000 purchase, 20% down payment, 30-year fixed, 360 payments, rate 6.875%, "
            "APR 7.012% as of 11/19/2026. Your terms will vary. Not an offer of credit."))
        for t in ("Payments of $2,661 a month on this example loan.", "Rates as low as 6.875%!"):
            rep = compliance.autofix(t, profile=prof)
            self.assertEqual(rep.verdict, "PASS", rep.summary())
            self.assertNotIn("Freddie Mac PMMS weekly national averages", rep.text)

    def test_own_rate_offer_needs_apr(self):
        rep = compliance.check("Rates as low as 6.25% this week only!", profile=PROFILE)
        self.assertIn("REGZ-RATE-OFFER-APR", ids(rep))
        self.assertEqual(compliance.autofix("Rates as low as 6.25% this week only!", profile=PROFILE).verdict, "FAIL")

    def test_missing_apr_example_is_named(self):
        rep = compliance.check("Just $1,200/mo", profile=PROFILE)
        f = next(f for f in rep.findings if f.rule_id == "REGZ-PAYMENT-TRIGGER")
        self.assertIn("apr_disclosure", f.missing_profile)


class SurveyPost(unittest.TestCase):
    TEXT = "Freddie Mac's survey: the 30-year fixed averaged 7.28% this week, up from 7.11%."

    def test_survey_post_passes_after_fixes(self):
        rep = compliance.autofix(self.TEXT, profile=PROFILE)
        self.assertEqual(rep.verdict, "PASS", rep.summary())
        applied = " ".join(rep.applied)
        for rid in ("RATE-AVERAGE-LABEL", "NMLS-ID", "EQUAL-HOUSING"):
            self.assertIn(rid, applied)
        self.assertIn("NMLS #1999001", rep.text)

    def test_without_nmls_in_profile_it_fails(self):
        thin = {k: v for k, v in PROFILE.items() if k != "nmls_id"}
        self.assertEqual(compliance.autofix(self.TEXT, profile=thin).verdict, "FAIL")


class Claims(unittest.TestCase):
    def test_guarantee_blocked(self):
        rep = compliance.autofix("We guarantee your approval, no credit check!", profile=PROFILE)
        self.assertEqual(rep.verdict, "FAIL")
        self.assertIn("MAP-GUARANTEE", ids(rep))

    def test_flags(self):
        cases = {"Perfect for young families: let's talk loans": "FAIR-LENDING-WORDS",
                 "Rates will drop next month, buy now": "MAP-FORECAST",
                 "Send me your buyers and I'll cover your ads": "RESPA-REFERRAL",
                 "Lowest rates in town!": "SUPERLATIVE-UNPROVEN"}
        for text, rid in cases.items():
            rep = compliance.autofix(text, profile=PROFILE)
            self.assertIn(rid, ids(rep), text)
            self.assertIn(rep.verdict, ("REVIEW", "FAIL"))

    def test_more_violations_caught(self):
        cases = {"Perfect for first-time buyers and young families!": "FAIR-LENDING-WORDS",
                 "Pre-approved in 24 hours, guaranteed.": "MAP-GUARANTEE",
                 "We guarantee you'll close on time.": "MAP-GUARANTEE",
                 "Rates will probably drop next month": "MAP-FORECAST",
                 "Talk to your mortgage counselor today": "REGZ-COUNSELOR",
                 "The government wants you to own a home": "MAP-GOVERNMENT"}
        for text, rid in cases.items():
            self.assertIn(rid, ids(compliance.check(text, profile=PROFILE)), text)

    def test_no_false_positives(self):
        for t in ("Lowest rates in months this week, per Freddie Mac.", "Fixed or adjustable? Here's how to choose.",
                  "Home prices rose this year in Travis County."):
            rep = compliance.check(t, profile=PROFILE)
            self.assertFalse({"SUPERLATIVE-UNPROVEN", "MAP-FIXED", "RATE-AVERAGE-LABEL"} & ids(rep), t)

    def test_both_nmls_ids_required(self):
        rep = compliance.check("Questions? Message me. Dana Whitfield NMLS #1999001", profile=PROFILE)
        self.assertIn("NMLS-ID", ids(rep))

    def test_plain_education_passes(self):
        rep = compliance.autofix("Pre-approval isn't a promise. It's a plan. Here's what we look at: income, "
                                 "assets, credit and the home. Message me with questions. Dana", profile=PROFILE)
        self.assertEqual(rep.verdict, "PASS", rep.summary())


class Pmms(unittest.TestCase):
    def setUp(self):
        self.rows = pmms.parse((FIX / "feeds" / pmms.FIXTURE).read_bytes())

    def test_latest_from_fixture(self):
        w = pmms.latest(self.rows)
        self.assertEqual((w["week_of"], w["rate_30"], w["rate_15"]), ("2026-11-19", "7.28", "6.66"))
        self.assertEqual((w["prev_rate_30"], w["change_30"]), ("7.11", "+0.17"))
        self.assertTrue(w["year_ago_rate_30"])

    def test_numbers_check_against_fixture(self):
        w = pmms.latest(self.rows)
        good = "The 30-year averaged 7.28%, up 0.17 points from 7.11%."
        self.assertEqual(provenance.unsupported_numbers(good, [w, {"t": "30-year"}]), [])
        self.assertEqual(provenance.unsupported_numbers("The 30-year averaged 7.3%.", [w, {"t": "30-year"}]),
                         ["7.3%"])


class Trigger(unittest.TestCase):
    def test_event_from_fixture(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("trigger", ROOT / "autopilot" / "trigger.py")
        trig = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(trig)
        evs = trig.events({}, fixtures=FIX / "feeds", today="2026-11-19")
        self.assertEqual([e["id"] for e in evs], ["pmms-2026-11-19"])
        self.assertEqual(trig.events({}, fixtures=FIX / "feeds", today="2026-12-01"), [])


if __name__ == "__main__":
    unittest.main()
