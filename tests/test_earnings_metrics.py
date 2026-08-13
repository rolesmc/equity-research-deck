#!/usr/bin/env python3
"""Tests for scripts/earnings_metrics.py.

The guard logic is what these protect: a ratio must never be invented to fill a
cell, and an absent input must never be silently treated as zero. Those are the
properties that make the output trustworthy, and they are the ones most likely
to break in a future edit.

Run:
    python3 -m unittest discover -s tests -v
    python3 tests/test_earnings_metrics.py
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(ROOT / "scripts"))

import earnings_metrics as em  # noqa: E402


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def metric(groups, label):
    """Find a metric by exact label across all groups."""
    for _, metrics in groups:
        for m in metrics:
            if m.label == label:
                return m
    raise AssertionError("no metric labelled {!r}".format(label))


def group_titles(groups):
    return [t for t, _ in groups]


# --------------------------------------------------------------- pure helpers


class TestHelpers(unittest.TestCase):
    def test_pct_change_normal(self):
        self.assertAlmostEqual(em.pct_change(150, 100), 50.0)

    def test_pct_change_refuses_negative_base(self):
        # Growth off a negative base is meaningless, not a big number.
        self.assertIsNone(em.pct_change(-0.61, -0.34))

    def test_pct_change_refuses_zero_base(self):
        self.assertIsNone(em.pct_change(100, 0))

    def test_pct_change_refuses_missing(self):
        self.assertIsNone(em.pct_change(100, None))
        self.assertIsNone(em.pct_change(None, 100))

    def test_safe_div_by_zero(self):
        self.assertIsNone(em.safe_div(10, 0))
        self.assertIsNone(em.safe_div(10, None))

    def test_num_rejects_bool(self):
        # True would otherwise arithmetic as 1 and corrupt a ratio.
        self.assertFalse(em.num(True))
        self.assertTrue(em.num(0))
        self.assertTrue(em.num(1.5))

    def test_fmt_money_scales_and_signs(self):
        self.assertEqual(em.fmt_money(48_000_000_000), "$48.00B")
        self.assertEqual(em.fmt_money(-8_560_000_000), "-$8.56B")
        self.assertEqual(em.fmt_money(900_000_000), "$900.00M")
        self.assertEqual(em.fmt_money(250), "$250.00")

    def test_g_treats_none_as_absent(self):
        d = {"a": {"b": None, "c": 0}}
        self.assertIsNone(em.g(d, "a", "b"))
        self.assertEqual(em.g(d, "a", "c"), 0)      # zero is a real value
        self.assertIsNone(em.g(d, "a", "missing"))


# --------------------------------------------------------- profitable company


class TestProfitable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups, cls.missing = em.compute(load("profitable.json"))

    def test_all_groups_present(self):
        self.assertEqual(len(group_titles(self.groups)), 8)

    def test_no_missing_inputs(self):
        self.assertEqual(self.missing, [])

    def test_enterprise_value(self):
        # 63,000M market cap + 900M debt - 3,100M cash = 60,800M
        self.assertAlmostEqual(metric(self.groups, "Enterprise value").value,
                               60_800_000_000)

    def test_net_debt_is_negative_when_cash_exceeds_debt(self):
        self.assertAlmostEqual(metric(self.groups, "Net debt").value,
                               -2_200_000_000)

    def test_trailing_pe(self):
        self.assertAlmostEqual(
            metric(self.groups, "P/E, trailing twelve months").value,
            210.0 / 2.05, places=4)

    def test_peg_uses_forward_pe(self):
        # forward P/E 210/2.85 = 73.684, ÷ 28% growth = 2.632
        self.assertAlmostEqual(metric(self.groups, "PEG ratio").value,
                               (210.0 / 2.85) / 28.0, places=4)

    def test_revenue_growth(self):
        self.assertAlmostEqual(metric(self.groups, "Revenue growth, YoY").value,
                               100 / 3, places=4)

    def test_rule_of_40_all_three_variants_present_and_distinct(self):
        fcf = metric(self.groups, "Rule of 40 — FCF variant").value
        ebitda = metric(self.groups, "Rule of 40 — EBITDA variant").value
        op = metric(self.groups, "Rule of 40 — operating variant").value
        # growth 33.33 + margins 27 / 25 / 18
        self.assertAlmostEqual(fcf, 100 / 3 + 27.0, places=3)
        self.assertAlmostEqual(ebitda, 100 / 3 + 25.0, places=3)
        self.assertAlmostEqual(op, 100 / 3 + 18.0, places=3)
        self.assertEqual(len({round(fcf, 3), round(ebitda, 3), round(op, 3)}), 3)

    def test_fcf_derived_from_ocf_minus_capex(self):
        self.assertAlmostEqual(metric(self.groups, "Free cash flow").value,
                               360_000_000 - 36_000_000)

    def test_interest_coverage(self):
        m = metric(self.groups, "Interest coverage")
        self.assertAlmostEqual(m.value, 216.0 / 12.0)
        self.assertEqual(m.flag, "good")

    def test_cash_conversion(self):
        self.assertAlmostEqual(
            metric(self.groups, "Cash conversion (OCF / net income)").value, 2.0)

    def test_eps_growth_computes_on_positive_base(self):
        self.assertAlmostEqual(metric(self.groups, "EPS growth, YoY").value,
                               (0.60 - 0.41) / 0.41 * 100, places=4)

    def test_magic_number(self):
        self.assertAlmostEqual(metric(self.groups, "Magic number").value,
                               255.0 / 300.0, places=4)


# --------------------------------------------------------- loss-making company


class TestLossMaking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups, cls.missing = em.compute(load("loss_making.json"))

    def test_trailing_pe_is_nm_on_a_loss(self):
        m = metric(self.groups, "P/E, trailing twelve months")
        self.assertEqual(m.value, em.NM)
        self.assertIn("negative", m.note)

    def test_forward_pe_still_computes(self):
        # Forward EPS is positive even though trailing is not.
        self.assertAlmostEqual(metric(self.groups, "P/E, forward").value,
                               101.0 / 0.85, places=4)

    def test_eps_growth_is_nm_off_negative_base(self):
        m = metric(self.groups, "EPS growth, YoY")
        self.assertEqual(m.value, em.NM)
        self.assertIn("negative", m.note)

    def test_ev_fcf_is_nm_when_input_absent(self):
        m = metric(self.groups, "EV / FCF, trailing")
        self.assertEqual(m.value, em.NM)

    def test_absent_ttm_fcf_is_reported_missing(self):
        # The n/m above must be explained by an entry in the missing list —
        # otherwise the report contradicts itself.
        self.assertTrue(any("free_cash_flow" in x for x in self.missing),
                        "missing list should name the unsupplied TTM FCF")

    def test_cash_conversion_is_nm_on_negative_net_income(self):
        self.assertEqual(
            metric(self.groups, "Cash conversion (OCF / net income)").value, em.NM)

    def test_free_cash_flow_is_negative_and_flagged(self):
        m = metric(self.groups, "Free cash flow")
        self.assertLess(m.value, 0)
        self.assertEqual(m.flag, "bad")

    def test_interest_coverage_below_one_is_flagged_bad(self):
        m = metric(self.groups, "Interest coverage")
        self.assertLess(m.value, 1.0)
        self.assertEqual(m.flag, "bad")

    def test_rule_of_40_variants_diverge_wildly(self):
        # The headline reason the script prints all three: a capex-heavy
        # business fails on FCF and passes on EBITDA in the same quarter.
        fcf = metric(self.groups, "Rule of 40 — FCF variant").value
        ebitda = metric(self.groups, "Rule of 40 — EBITDA variant").value
        self.assertLess(fcf, 0)
        self.assertGreater(ebitda, 40)

    def test_ev_uses_debt_not_market_cap(self):
        self.assertAlmostEqual(metric(self.groups, "Enterprise value").value,
                               48e9 + 35e9 - 6.9e9)


# --------------------------------------------------------- declining company


class TestDeclining(unittest.TestCase):
    """Guards that the other two fixtures leave uncovered."""

    @classmethod
    def setUpClass(cls):
        cls.groups, cls.missing = em.compute(load("declining.json"))

    def test_peg_is_nm_on_negative_growth(self):
        # Trailing EPS is positive, so a P/E exists — the only thing stopping
        # PEG is the negative growth rate. This is the guard most likely to be
        # optimised away by someone "simplifying" the branch.
        m = metric(self.groups, "PEG ratio")
        self.assertEqual(m.value, em.NM)
        self.assertIn("negative", m.note)

    def test_trailing_pe_still_computes(self):
        # Confirms the PEG n/m above is caused by growth, not by a missing P/E.
        self.assertAlmostEqual(
            metric(self.groups, "P/E, trailing twelve months").value,
            18.0 / 0.34, places=4)

    def test_ev_ebitda_is_nm_on_negative_ebitda(self):
        m = metric(self.groups, "EV / EBITDA, trailing")
        self.assertEqual(m.value, em.NM)
        self.assertIn("EBITDA", m.note)

    def test_ev_fcf_is_nm_on_negative_fcf(self):
        self.assertEqual(metric(self.groups, "EV / FCF, trailing").value, em.NM)

    def test_revenue_decline_is_a_number_not_nm(self):
        # A negative growth rate is meaningful; only a negative *base* is not.
        m = metric(self.groups, "Revenue growth, YoY")
        self.assertAlmostEqual(m.value, -20.0, places=4)
        self.assertEqual(m.flag, "warn")

    def test_eps_growth_is_negative_not_nm(self):
        # Prior-year EPS is positive, so the decline to a loss is computable.
        self.assertLess(metric(self.groups, "EPS growth, YoY").value, 0)

    def test_roe_is_nm_on_negative_equity(self):
        m = metric(self.groups, "Return on equity (ROE)")
        self.assertEqual(m.value, em.NM)
        self.assertIn("negative denominator", m.note)

    def test_net_debt_ebitda_is_nm_on_negative_ebitda(self):
        self.assertEqual(metric(self.groups, "Net debt / EBITDA").value, em.NM)

    def test_interest_coverage_negative_is_flagged_bad(self):
        m = metric(self.groups, "Interest coverage")
        self.assertLess(m.value, 0)
        self.assertEqual(m.flag, "bad")

    def test_quick_ratio_excludes_inventory(self):
        cur = metric(self.groups, "Current ratio").value
        quick = metric(self.groups, "Quick ratio").value
        self.assertLess(quick, cur)
        self.assertAlmostEqual(quick, (610 - 260) / 740, places=4)

    def test_rule_of_40_is_deeply_negative(self):
        self.assertLess(metric(self.groups, "Rule of 40 — EBITDA variant").value, 0)


# ------------------------------------------------------------- empty input


class TestEmptyInput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups, cls.missing = em.compute(load("empty.json"))

    def test_absent_debt_is_nm_not_zero(self):
        # The regression this exists to prevent: rendering $0.00 for a balance
        # sheet that was never supplied fabricates a fact.
        self.assertEqual(metric(self.groups, "Total debt").value, em.NM)
        self.assertEqual(metric(self.groups, "Cash & equivalents").value, em.NM)

    def test_ev_is_nm_without_a_balance_sheet(self):
        m = metric(self.groups, "Enterprise value")
        self.assertEqual(m.value, em.NM)
        self.assertIn("balance sheet", m.note.lower())

    def test_nothing_is_invented_anywhere(self):
        for title, metrics in self.groups:
            for m in metrics:
                self.assertIn(m.value, (em.NM,),
                              "{} / {} produced {!r} from no input".format(
                                  title, m.label, m.value))

    def test_missing_list_is_populated(self):
        self.assertGreater(len(self.missing), 3)


# ----------------------------------------------------------------- rendering


class TestRendering(unittest.TestCase):
    def test_json_output_is_valid_and_marks_meaningfulness(self):
        data = load("loss_making.json")
        groups, missing = em.compute(data)
        payload = json.loads(em.render_json(data, groups, missing))
        self.assertIn("groups", payload)
        pe = payload["groups"]["Valuation"]["P/E, trailing twelve months"]
        self.assertFalse(pe["meaningful"])
        self.assertIsNone(pe["value"])
        self.assertEqual(pe["display"], em.NM)

    def test_brief_tier_trims_groups(self):
        data = load("profitable.json")
        groups, missing = em.compute(data)
        brief = em.render_text(data, groups, missing, "brief")
        standard = em.render_text(data, groups, missing, "standard")
        self.assertLess(len(brief), len(standard))
        self.assertNotIn("CASH QUALITY", brief)
        self.assertIn("VALUATION", brief)

    def test_text_output_carries_period_and_as_of(self):
        data = load("profitable.json")
        groups, missing = em.compute(data)
        text = em.render_text(data, groups, missing, "standard")
        self.assertIn("Q2 FY2026", text)
        self.assertIn("2026-08-13", text)


# ----------------------------------------------------------------------- CLI


class TestCLI(unittest.TestCase):
    script = str(ROOT / "scripts" / "earnings_metrics.py")

    def run_cli(self, *args):
        return subprocess.run([sys.executable, self.script, *args],
                              capture_output=True, text=True)

    def test_schema_emits_valid_json(self):
        r = self.run_cli("--schema")
        self.assertEqual(r.returncode, 0)
        json.loads(r.stdout)

    def test_missing_file_exits_2(self):
        r = self.run_cli(str(FIXTURES / "does-not-exist.json"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("no such file", r.stderr)

    def test_malformed_json_exits_2_with_reason(self):
        bad = FIXTURES / "_tmp_malformed.json"
        bad.write_text("not json at all", encoding="utf-8")
        try:
            r = self.run_cli(str(bad))
            self.assertEqual(r.returncode, 2)
            self.assertIn("invalid JSON", r.stderr)
        finally:
            bad.unlink()

    def test_no_args_errors(self):
        r = self.run_cli()
        self.assertNotEqual(r.returncode, 0)

    def test_each_fixture_runs_clean_at_every_tier(self):
        for fx in ("profitable.json", "loss_making.json",
                   "declining.json", "empty.json"):
            for tier in ("brief", "standard", "deep"):
                with self.subTest(fixture=fx, tier=tier):
                    r = self.run_cli(str(FIXTURES / fx), "--tier", tier)
                    self.assertEqual(r.returncode, 0, r.stderr)
                    self.assertIn("n/m = not meaningful", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
