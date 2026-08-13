#!/usr/bin/env python3
"""Compute the earnings metric suite from a filled input file.

Takes the figures you pulled from an earnings release and derives the ratios,
margins, growth rates, and quality metrics that belong in an earnings deck —
with the guards that stop the classic errors: P/E on a loss, PEG on negative
growth, EV/EBITDA on negative EBITDA, Rule of 40 without stating its variant.

Anything it cannot compute is reported as n/m (not meaningful) with the reason,
never as a number. Anything missing from the input is listed at the end so you
know what to go find.

Usage:
    python3 scripts/earnings_metrics.py input.json
    python3 scripts/earnings_metrics.py input.json --format json
    python3 scripts/earnings_metrics.py input.json --tier brief
    python3 scripts/earnings_metrics.py --schema > my-company.json

Standard library only.
"""

import argparse
import json
import sys
from pathlib import Path

# ------------------------------------------------------------------ schema

SCHEMA = {
    "company": {
        "name": "Example Corp", "ticker": "EXMP",
        "period": "Q2 FY2026", "as_of": "2026-08-12", "currency": "USD",
    },
    "market": {
        "price": 101.00,
        "shares_diluted": 475_000_000,
        "market_cap": 48_000_000_000,
    },
    "income_statement": {
        "revenue": 2_580_000_000,
        "revenue_prior_year": 1_290_000_000,
        "revenue_prior_quarter": 2_100_000_000,
        "gross_profit": 1_780_000_000,
        "operating_income": 128_000_000,
        "net_income": -290_000_000,
        "ebitda": 1_150_000_000,
        "interest_expense": 640_000_000,
        "eps_diluted": -0.61,
        "eps_diluted_prior_year": -0.34,
        "stock_based_comp": 210_000_000,
    },
    "balance_sheet": {
        "cash_and_equivalents": 6_900_000_000,
        "total_debt": 35_000_000_000,
        "total_equity": 4_100_000_000,
        "total_assets": 52_000_000_000,
        "current_assets": 9_800_000_000,
        "current_liabilities": 7_400_000_000,
        "inventory": 0,
        "receivables": 2_200_000_000,
    },
    "cash_flow": {
        "operating_cash_flow": 1_240_000_000,
        "capex": 9_800_000_000,
    },
    "forward": {
        "eps_next_year": 0.85,
        "revenue_next_year": 19_000_000_000,
        "eps_growth_pct": 42.0,
        "_comment": "eps_growth_pct drives PEG. Use consensus or your own — say which.",
    },
    "recurring": {
        "_comment": "Optional. Only for subscription / recurring-revenue businesses.",
        "arr": None,
        "net_revenue_retention_pct": None,
        "sales_and_marketing": None,
        "new_arr_added": None,
    },
    "_meta": {
        "trailing_twelve_month": {
            "_comment": "Optional but strongly preferred — quarterly P/E is noisy.",
            "revenue": 9_100_000_000,
            "net_income": -980_000_000,
            "eps_diluted": -2.10,
            "ebitda": 3_900_000_000,
            "free_cash_flow": None,
        }
    },
}

NM = "n/m"


# ------------------------------------------------------------------ helpers

def g(d, *path, default=None):
    """Nested get that treats None and '' as absent."""
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    if cur is None or cur == "":
        return default
    return cur


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


class Metric:
    __slots__ = ("label", "value", "unit", "note", "flag")

    def __init__(self, label, value, unit="", note="", flag=""):
        self.label = label
        self.value = value
        self.unit = unit
        self.note = note
        self.flag = flag          # "", "good", "warn", "bad"

    @property
    def display(self):
        if self.value == NM:
            return NM
        if not num(self.value):
            return str(self.value)
        v = self.value
        if self.unit == "%":
            return "{:,.1f}%".format(v)
        if self.unit == "x":
            return "{:,.1f}x".format(v)
        if self.unit == "$":
            return fmt_money(v)
        if self.unit == "d":
            return "{:,.0f} days".format(v)
        return "{:,.2f}".format(v)


def fmt_money(v):
    a = abs(v)
    for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if a >= div:
            return "{}${:,.2f}{}".format("-" if v < 0 else "", a / div, suf)
    return "{}${:,.2f}".format("-" if v < 0 else "", a)


def pct_change(new, old):
    if not (num(new) and num(old)) or old == 0:
        return None
    if old < 0:
        return None            # growth off a negative base is meaningless
    return (new - old) / old * 100.0


def safe_div(a, b):
    if not (num(a) and num(b)) or b == 0:
        return None
    return a / b


# ------------------------------------------------------------------ compute

def compute(data):
    """Returns (groups, missing). groups = [(title, [Metric, ...]), ...]"""
    missing = []

    def need(label, *path):
        v = g(data, *path)
        if v is None:
            missing.append("{}  ({})".format(label, ".".join(path)))
        return v

    # --- inputs
    price = g(data, "market", "price")
    mcap = g(data, "market", "market_cap")
    shares = g(data, "market", "shares_diluted")
    if mcap is None and num(price) and num(shares):
        mcap = price * shares

    # Absent is not zero. Track presence separately so a balance sheet we were
    # never given renders n/m rather than a fabricated $0.00.
    cash_given = g(data, "balance_sheet", "cash_and_equivalents")
    debt_given = g(data, "balance_sheet", "total_debt")
    cash = cash_given if num(cash_given) else 0
    debt = debt_given if num(debt_given) else 0
    if not num(cash_given):
        missing.append("Cash & equivalents  (balance_sheet.cash_and_equivalents)")
    if not num(debt_given):
        missing.append("Total debt  (balance_sheet.total_debt)")
    equity = g(data, "balance_sheet", "total_equity")
    assets = g(data, "balance_sheet", "total_assets")
    cur_a = g(data, "balance_sheet", "current_assets")
    cur_l = g(data, "balance_sheet", "current_liabilities")
    inv = g(data, "balance_sheet", "inventory", default=0)
    recv = g(data, "balance_sheet", "receivables")

    rev = need("Revenue", "income_statement", "revenue")
    rev_py = g(data, "income_statement", "revenue_prior_year")
    rev_pq = g(data, "income_statement", "revenue_prior_quarter")
    gross = g(data, "income_statement", "gross_profit")
    op_inc = g(data, "income_statement", "operating_income")
    net_inc = g(data, "income_statement", "net_income")
    ebitda = g(data, "income_statement", "ebitda")
    interest = g(data, "income_statement", "interest_expense")
    eps = g(data, "income_statement", "eps_diluted")
    eps_py = g(data, "income_statement", "eps_diluted_prior_year")
    sbc = g(data, "income_statement", "stock_based_comp")

    ocf = g(data, "cash_flow", "operating_cash_flow")
    capex = g(data, "cash_flow", "capex")
    fcf = g(data, "cash_flow", "free_cash_flow")
    if fcf is None and num(ocf) and num(capex):
        fcf = ocf - abs(capex)

    ttm = g(data, "_meta", "trailing_twelve_month", default={})
    ttm_rev = g(ttm, "revenue")
    ttm_ni = g(ttm, "net_income")
    ttm_eps = g(ttm, "eps_diluted")
    ttm_ebitda = g(ttm, "ebitda")
    ttm_fcf = g(ttm, "free_cash_flow")

    fwd_eps = g(data, "forward", "eps_next_year")
    fwd_growth = g(data, "forward", "eps_growth_pct")

    ev = None
    if num(mcap):
        ev = mcap + (debt or 0) - (cash or 0)

    groups = []

    # --- capital structure
    bs_given = num(debt_given) and num(cash_given)
    cap = [
        Metric("Market capitalization", mcap if num(mcap) else NM, "$"),
        Metric("Total debt", debt_given if num(debt_given) else NM, "$"),
        Metric("Cash & equivalents", cash_given if num(cash_given) else NM, "$"),
        Metric("Net debt", (debt - cash) if bs_given else NM, "$",
               "" if bs_given else "needs both debt and cash"),
        Metric("Enterprise value", ev if (num(ev) and bs_given) else NM, "$",
               "market cap + debt − cash — use this for every multiple"
               if bs_given else "balance sheet not supplied; EV cannot be trusted"),
    ]
    groups.append(("Capital structure", cap))

    # --- growth
    yoy = pct_change(rev, rev_py)
    qoq = pct_change(rev, rev_pq)
    eps_growth = pct_change(eps, eps_py)
    grow = [
        Metric("Revenue growth, YoY", yoy if yoy is not None else NM, "%",
               "" if yoy is not None else "needs revenue_prior_year > 0",
               flag="good" if (yoy or 0) > 25 else ("warn" if (yoy or 0) < 5 else "")),
        Metric("Revenue growth, QoQ", qoq if qoq is not None else NM, "%"),
    ]
    if num(eps) and num(eps_py) and eps_py > 0:
        grow.append(Metric("EPS growth, YoY", eps_growth, "%"))
    elif num(eps) and num(eps_py):
        grow.append(Metric("EPS growth, YoY", NM, "",
                           "prior-year EPS is negative — growth rate is meaningless"))
    if num(qoq):
        grow.append(Metric("Annualized run-rate", rev * 4, "$",
                           "current quarter × 4 — not a forecast"))
    groups.append(("Growth", grow))

    # --- margins
    def margin(nm_, val):
        m = safe_div(val, rev)
        return Metric(nm_, m * 100 if m is not None else NM, "%")

    marg = [
        margin("Gross margin", gross),
        margin("Operating margin", op_inc),
        margin("Net margin", net_inc),
        margin("EBITDA margin", ebitda),
        margin("FCF margin", fcf),
    ]
    if num(sbc) and num(rev):
        r = sbc / rev * 100
        marg.append(Metric("SBC as % of revenue", r, "%",
                           "dilution cost — above 15% is heavy",
                           flag="bad" if r > 20 else ("warn" if r > 10 else "")))
    groups.append(("Margins", marg))

    # --- valuation
    val = []

    def pe(label, e, basis):
        if not num(e):
            val.append(Metric(label, NM, "", "no {} available".format(basis)))
        elif e <= 0:
            val.append(Metric(label, NM, "", "{} is negative — P/E undefined on a loss".format(basis)))
        elif not num(price):
            val.append(Metric(label, NM, "", "no price"))
        else:
            val.append(Metric(label, price / e, "x"))

    pe("P/E, trailing twelve months", ttm_eps, "TTM EPS")
    pe("P/E, forward", fwd_eps, "forward EPS")

    # PEG — the most misused ratio in equity research
    trailing_pe = safe_div(price, ttm_eps) if (num(ttm_eps) and ttm_eps > 0) else None
    fwd_pe = safe_div(price, fwd_eps) if (num(fwd_eps) and fwd_eps > 0) else None
    peg_pe = fwd_pe if fwd_pe is not None else trailing_pe
    if peg_pe is None:
        val.append(Metric("PEG ratio", NM, "", "no positive P/E to divide"))
    elif not num(fwd_growth):
        val.append(Metric("PEG ratio", NM, "", "no forward EPS growth rate supplied"))
    elif fwd_growth <= 0:
        val.append(Metric("PEG ratio", NM, "", "growth is zero or negative — PEG is undefined"))
    else:
        p = peg_pe / fwd_growth
        val.append(Metric("PEG ratio", p, "x",
                          "P/E ÷ EPS growth %; under 1.0 is the classic 'cheap' threshold",
                          flag="good" if p < 1 else ("warn" if p > 2 else "")))

    for label, denom, basis in (
        ("P/S, trailing", ttm_rev, "TTM revenue"),
        ("P/S, annualized quarter", rev * 4 if num(rev) else None, "quarter × 4"),
    ):
        r = safe_div(mcap, denom)
        val.append(Metric(label, r if r is not None else NM, "x",
                          "" if r is not None else "no " + basis))

    for label, denom, guard in (
        ("EV / Sales, trailing", ttm_rev, None),
        ("EV / EBITDA, trailing", ttm_ebitda, "EBITDA"),
        ("EV / FCF, trailing", ttm_fcf, "FCF"),
    ):
        if num(denom) and denom > 0 and num(ev):
            val.append(Metric(label, ev / denom, "x"))
        elif num(denom) and denom <= 0:
            val.append(Metric(label, NM, "", "{} is negative".format(guard or "denominator")))
        else:
            val.append(Metric(label, NM, "", "input not supplied"))

    r = safe_div(mcap, equity)
    val.append(Metric("P/B", r if r is not None else NM, "x"))

    if num(ttm_fcf) and num(mcap) and mcap > 0:
        val.append(Metric("FCF yield", ttm_fcf / mcap * 100, "%",
                          "inverse of EV/FCF on equity value"))
    groups.append(("Valuation", val))

    # --- returns
    ret = []
    for label, n_, d_, note in (
        ("Return on equity (ROE)", ttm_ni if num(ttm_ni) else net_inc, equity, "TTM if supplied"),
        ("Return on assets (ROA)", ttm_ni if num(ttm_ni) else net_inc, assets, ""),
    ):
        r = safe_div(n_, d_)
        if r is None:
            ret.append(Metric(label, NM, "", "input not supplied"))
        elif num(d_) and d_ < 0:
            ret.append(Metric(label, NM, "", "negative denominator"))
        else:
            ret.append(Metric(label, r * 100, "%", note))
    invested = None
    if num(debt) and num(equity):
        invested = debt + equity
    r = safe_div(op_inc, invested)
    ret.append(Metric("Return on invested capital (pre-tax)",
                      r * 100 if r is not None else NM, "%",
                      "operating income ÷ (debt + equity)"))
    groups.append(("Returns", ret))

    # --- Rule of 40 (state the variant, always)
    r40 = []
    if yoy is not None:
        fcf_m = safe_div(fcf, rev)
        ebitda_m = safe_div(ebitda, rev)
        op_m = safe_div(op_inc, rev)
        for label, m, variant in (
            ("Rule of 40 — FCF variant", fcf_m, "growth % + FCF margin %"),
            ("Rule of 40 — EBITDA variant", ebitda_m, "growth % + EBITDA margin %"),
            ("Rule of 40 — operating variant", op_m, "growth % + operating margin %"),
        ):
            if m is None:
                r40.append(Metric(label, NM, "", "margin input not supplied"))
                continue
            score = yoy + m * 100
            r40.append(Metric(label, score, "",
                              variant + " — 40 is the pass mark",
                              flag="good" if score >= 40 else "warn"))
    else:
        r40.append(Metric("Rule of 40", NM, "", "needs a valid YoY growth rate"))
    nrr = g(data, "recurring", "net_revenue_retention_pct")
    if num(nrr):
        r40.append(Metric("Net revenue retention", nrr, "%",
                          "above 120% is best-in-class",
                          flag="good" if nrr >= 120 else ("bad" if nrr < 100 else "warn")))
    sm = g(data, "recurring", "sales_and_marketing")
    new_arr = g(data, "recurring", "new_arr_added")
    r = safe_div(new_arr, sm)
    if r is not None:
        r40.append(Metric("Magic number", r, "x",
                          "new ARR ÷ S&M spend; above 0.75 justifies more spend",
                          flag="good" if r > 0.75 else "warn"))
    groups.append(("Efficiency & Rule of 40", r40))

    # --- leverage and liquidity
    lev = []
    nd = (debt - cash) if (num(debt) and num(cash)) else None
    base_ebitda = ttm_ebitda if num(ttm_ebitda) else (ebitda * 4 if num(ebitda) else None)
    if num(nd) and num(base_ebitda) and base_ebitda > 0:
        r = nd / base_ebitda
        lev.append(Metric("Net debt / EBITDA", r, "x",
                          "above 4x is stressed for most non-financials",
                          flag="bad" if r > 4 else ("warn" if r > 2.5 else "good")))
    else:
        lev.append(Metric("Net debt / EBITDA", NM, "",
                          "negative or missing EBITDA"))
    if num(op_inc) and num(interest) and interest > 0:
        r = op_inc / interest
        lev.append(Metric("Interest coverage", r, "x",
                          "operating income ÷ interest expense; below 1.0 means "
                          "operations do not cover the interest bill",
                          flag="bad" if r < 1 else ("warn" if r < 3 else "good")))
    else:
        lev.append(Metric("Interest coverage", NM, "", "input not supplied"))
    r = safe_div(debt, equity)
    lev.append(Metric("Debt / equity", r if r is not None else NM, "x"))
    r = safe_div(cur_a, cur_l)
    lev.append(Metric("Current ratio", r if r is not None else NM, "x",
                      flag="warn" if (r or 99) < 1 else ""))
    if num(cur_a) and num(inv) and num(cur_l) and cur_l:
        lev.append(Metric("Quick ratio", (cur_a - inv) / cur_l, "x"))
    groups.append(("Leverage & liquidity", lev))

    # --- cash quality
    q = []
    r = safe_div(ocf, net_inc)
    if r is not None and num(net_inc) and net_inc > 0:
        q.append(Metric("Cash conversion (OCF / net income)", r, "x",
                        "below 1.0 means earnings are not turning into cash",
                        flag="warn" if r < 1 else "good"))
    else:
        q.append(Metric("Cash conversion (OCF / net income)", NM, "",
                        "net income is negative or missing"))
    q.append(Metric("Operating cash flow", ocf if num(ocf) else NM, "$"))
    q.append(Metric("Capital expenditure", -abs(capex) if num(capex) else NM, "$"))
    q.append(Metric("Free cash flow", fcf if num(fcf) else NM, "$",
                    "OCF − capex", flag="bad" if (num(fcf) and fcf < 0) else ""))
    if num(fcf) and num(capex) and fcf < 0 and abs(capex) > 0:
        q.append(Metric("Capex intensity", abs(capex) / rev * 100 if num(rev) else NM, "%",
                        "capex as % of revenue — the reason FCF is negative"))
    if num(recv) and num(rev) and rev:
        q.append(Metric("Days sales outstanding", recv / (rev / 91.25), "d"))
    groups.append(("Cash quality", q))

    for label, path in (
        ("TTM revenue", ("_meta", "trailing_twelve_month", "revenue")),
        ("TTM EPS", ("_meta", "trailing_twelve_month", "eps_diluted")),
        ("TTM EBITDA", ("_meta", "trailing_twelve_month", "ebitda")),
        ("TTM free cash flow", ("_meta", "trailing_twelve_month", "free_cash_flow")),
        ("Forward EPS", ("forward", "eps_next_year")),
        ("Forward EPS growth %", ("forward", "eps_growth_pct")),
    ):
        if g(data, *path) is None:
            missing.append("{}  ({})".format(label, ".".join(path)))

    return groups, missing


# ------------------------------------------------------------------ output

TIERS = {
    "brief": {"Capital structure", "Growth", "Valuation", "Efficiency & Rule of 40"},
    "standard": None,
    "deep": None,
}

FLAG_MARK = {"good": "+", "warn": "!", "bad": "x", "": " "}


def render_text(data, groups, missing, tier):
    c = data.get("company", {})
    out = []
    out.append("")
    out.append("  {}  ({})".format(c.get("name", "—"), c.get("ticker", "—")))
    out.append("  {}   ·   figures as of {}   ·   {}".format(
        c.get("period", "—"), c.get("as_of", "—"), c.get("currency", "USD")))
    out.append("  " + "─" * 66)

    keep = TIERS.get(tier)
    for title, metrics in groups:
        if keep is not None and title not in keep:
            continue
        out.append("")
        out.append("  {}".format(title.upper()))
        for m in metrics:
            mark = FLAG_MARK.get(m.flag, " ")
            line = "   {} {:<38} {:>14}".format(mark, m.label, m.display)
            out.append(line)
            if m.note and (m.value == NM or tier == "deep"):
                out.append("       {}".format(m.note))

    out.append("")
    out.append("  " + "─" * 66)
    if missing:
        out.append("  NOT SUPPLIED — metrics above marked n/m depend on these:")
        for x in sorted(set(missing)):
            out.append("     · {}".format(x))
    else:
        out.append("  All inputs supplied.")
    out.append("")
    out.append("  n/m = not meaningful. A ratio is never invented to fill a cell.")
    out.append("  Legend:  + favourable   ! watch   x adverse")
    out.append("")
    return "\n".join(out)


def render_json(data, groups, missing):
    payload = {
        "company": data.get("company", {}),
        "groups": {
            title: {
                m.label: {
                    "value": None if m.value == NM else m.value,
                    "display": m.display,
                    "unit": m.unit,
                    "note": m.note,
                    "flag": m.flag,
                    "meaningful": m.value != NM,
                } for m in metrics
            } for title, metrics in groups
        },
        "missing_inputs": sorted(set(missing)),
    }
    return json.dumps(payload, indent=2)


# ------------------------------------------------------------------ driver

def main():
    ap = argparse.ArgumentParser(
        description="Compute the earnings metric suite from an input file.")
    ap.add_argument("file", nargs="?", help="path to the filled input JSON")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--tier", choices=("brief", "standard", "deep"), default="standard",
                    help="brief trims to headline groups; deep prints every note")
    ap.add_argument("--schema", action="store_true",
                    help="print a blank input file and exit")
    args = ap.parse_args()

    if args.schema:
        print(json.dumps(SCHEMA, indent=2))
        return 0
    if not args.file:
        ap.error("give an input file, or --schema to print a blank one")

    path = Path(args.file)
    if not path.is_file():
        print("earnings_metrics: no such file: {}".format(path), file=sys.stderr)
        return 2
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print("earnings_metrics: invalid JSON in {}: {}".format(path, e), file=sys.stderr)
        return 2

    groups, missing = compute(data)
    if args.format == "json":
        print(render_json(data, groups, missing))
    else:
        print(render_text(data, groups, missing, args.tier))
    return 0


if __name__ == "__main__":
    sys.exit(main())
