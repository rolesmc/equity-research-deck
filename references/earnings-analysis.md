# Earnings Analysis

The workflow for "pull the latest earnings on X and break it down." Produces a report at
one of three depths, ending in a TLDR, optionally rendered as a deck.

---

## Detail tiers

Ask once if the user hasn't said. Default to **standard**.

| Tier | Output | Slides | Metrics | Use when |
|------|--------|--------|---------|----------|
| **Brief** | One screen or 4 slides | 4 | ~12 headline | "How did they do?" / a name they're tracking casually |
| **Standard** | Full report or 11 slides | 11 | ~35 across 8 groups | The default. A position or a candidate |
| **Deep** | Extended report or 14–16 slides | 14–16 | Everything + segments, peers, history | A real allocation decision, or a thesis under review |

The tier changes depth, never honesty. A brief report still marks provenance, still names
the bear case in one line, still carries disclosure.

---

## Workflow

### 1. Pull the earnings

Primary sources, in this order:

1. **Earnings press release / 8-K** — the headline figures and guidance
2. **Investor presentation** — segment splits, unit economics, the metrics management chose
3. **Call transcript** — how they answered the hard question; forward color not in the release
4. **10-Q / 10-K** — balance sheet, debt, share count, SBC, accounting policy

Record the **reporting period, the filing date, and the fiscal calendar**. A "Q2" that ends
in June and a "Q2" that ends in October are not comparable, and fiscal years that lead the
calendar year (common in tech and retail) mis-sort constantly.

### 2. Fill the input file

```bash
python3 scripts/earnings_metrics.py --schema > work/TICKER.json
```

Fill what you have. **Leave anything you don't have as `null`** — the script reports it as
not-supplied rather than computing a wrong number from a zero.

Supply the `_meta.trailing_twelve_month` block whenever you can. Quarterly P/E and P/S are
noisy and seasonal; TTM is what analysts quote and what makes your figures comparable to
anything a reader looks up.

### 3. Compute

```bash
python3 scripts/earnings_metrics.py work/TICKER.json --tier standard
python3 scripts/earnings_metrics.py work/TICKER.json --format json   # to feed the deck
```

**Do the arithmetic here, not in your head.** The script exists because ratio errors in a
research document are unrecoverable — a reader who spots one stops trusting all of it.

### 4. Interpret

The script gives you numbers and guard rails. It does not give you the finding. Read
§ *Reading the output* below.

### 5. Report

Structure per § *Report structure*. Always end with the TLDR.

---

## The metric suite

### Valuation

| Metric | Formula | Read it as |
|--------|---------|-----------|
| **P/E (TTM)** | Price ÷ TTM diluted EPS | Undefined on a loss. The script returns n/m — do not substitute "adjusted" EPS without saying so |
| **P/E (forward)** | Price ÷ next-year EPS estimate | State whose estimate. Consensus and your own are different claims |
| **PEG** | P/E ÷ EPS growth % | Under 1.0 is the classic cheap threshold. Undefined on negative growth. **The most misused ratio in research** — see below |
| **P/S** | Market cap ÷ revenue | The fallback when there are no earnings. Ignores the balance sheet entirely |
| **EV/Sales** | EV ÷ revenue | P/S corrected for debt. Prefer it |
| **EV/EBITDA** | EV ÷ EBITDA | The standard for capital-intensive businesses. Undefined on negative EBITDA |
| **EV/FCF** | EV ÷ free cash flow | The hardest to game. Undefined when FCF is negative |
| **P/B** | Market cap ÷ equity | Meaningful for financials and asset-heavy names; near-useless for software |
| **FCF yield** | TTM FCF ÷ market cap | What the business throws off against what you pay |

**On PEG.** It is quoted constantly and correctly computed rarely. Three rules: it needs a
*positive* P/E and a *positive* forward growth rate; the growth rate must be forward, not
trailing; and it says nothing about a company whose growth is decelerating — a PEG of 0.8
on a growth rate about to halve is a trap, not a bargain. The script refuses to compute it
when the inputs don't support it. Respect the refusal.

### Growth

Revenue YoY and QoQ, EPS YoY, and the annualized run-rate. Two traps:

- **Growth off a negative base is meaningless.** The script returns n/m when prior-year
  EPS is negative. "EPS improved from −$0.34 to −$0.61" is a sentence; there is no percentage.
- **The run-rate is not a forecast.** Quarter × 4 ignores seasonality entirely. Label it as
  arithmetic, and never as guidance.

### Margins

Gross, operating, net, EBITDA, FCF. Plus **SBC as % of revenue** — the cost that doesn't
appear in adjusted numbers. Above 10% is heavy; above 20% means "adjusted" profitability
is substantially a story about not counting compensation.

### Rule of 40

Revenue growth % + margin %. **Always state the variant**, because they diverge wildly:

| Variant | Formula | Use for |
|---------|---------|---------|
| FCF | growth % + FCF margin % | The strictest and most common in SaaS |
| EBITDA | growth % + EBITDA margin % | Capital-intensive names where capex is a growth investment |
| Operating | growth % + operating margin % | GAAP-purist version |

A company building physical assets can score −230 on the FCF variant and +145 on the
EBITDA variant *in the same quarter*. Neither is wrong; quoting one without naming it is.
The script prints all three for exactly this reason.

Rule of 40 is a software heuristic. Applying it to a bank, a miner, or a utility produces
a number with no meaning — don't.

### Returns

ROE, ROA, pre-tax ROIC. All are meaningless on negative earnings, and ROE specifically is
flattered by leverage — a company can raise ROE purely by borrowing. Read it alongside
debt/equity or not at all.

### Leverage & liquidity

| Metric | Threshold |
|--------|-----------|
| Net debt / EBITDA | > 4x is stressed for most non-financials |
| **Interest coverage** | **< 1.0x means operations don't cover the interest bill** |
| Debt / equity | Sector-dependent; compare to peers, not to an absolute |
| Current / quick ratio | < 1.0 is a working-capital warning |

Interest coverage is the metric that matters most for anything financing growth with debt,
and it is the one retail coverage omits most often.

### Cash quality

**Cash conversion (OCF ÷ net income)** below 1.0 means earnings aren't becoming cash — the
single most reliable early warning of an accounting problem. Also capex intensity (why FCF
is negative) and DSO (whether revenue is being collected).

### Recurring-revenue extras

Net revenue retention (>120% is best-in-class, <100% means the base is shrinking) and the
magic number (new ARR ÷ S&M; >0.75 justifies more spend). Only for subscription businesses.

---

## Reading the output

The script flags `+` favourable, `!` watch, `x` adverse. Those are thresholds, not findings.
The finding comes from these questions:

**Which metrics disagree?** The most valuable output is a conflict. EBITDA margin strong
and FCF deeply negative means capex is eating everything — that is the story, and it only
appears when you read the groups against each other.

**What does n/m tell you?** A page of n/m is itself the finding: this company has no
earnings, no positive EBITDA, no cash flow, and can only be valued on revenue and a story.
Say that plainly rather than reaching for adjusted metrics that manufacture a ratio.

**Direction vs. level.** A margin that improved sequentially but is far below last year is
a turn, not a recovery. State both comparisons.

**What is the multiple assuming?** A forward P/E of 118x embeds an assumption. Name it.

---

## Report structure

### Brief (4 slides / one screen)

1. **The result** — 4 KPI tiles: revenue + growth, the profit line, the balance-sheet
   constraint, the one metric specific to this business
2. **The numbers** — ~12 metrics in one table, provenance-typed
3. **What moved and why** — three bullets, one of which is the bear case
4. **TLDR**

### Standard (11 slides)

The full arc in `deck-architecture.md`, with two changes for earnings mode:
- Slide 3 becomes the reported quarter with the KPI tiles
- Slide 11 ends with the **TLDR** before the monitoring table and disclosure

### Deep (14–16 slides)

Standard, plus:
- **Segment breakdown** — revenue and margin by segment, with the mix shift called out
- **Peer comparison** — the same 6–8 metrics for 2–3 genuine comparables, same basis
- **Multi-year history** — 8+ quarters of the metric the thesis turns on
- **Full ratio appendix** — every group the script produced, including the n/m rows

---

## The TLDR

Always last. Six lines, no more. It is what gets screenshotted and forwarded, so it has to
survive being read alone.

```
TLDR — [TICKER] [PERIOD]

  The number:     Revenue $2.58B, +100% YoY. Operating profit $128M, first positive quarter in a year.
  The catch:      Interest expense $640M against $128M of operating profit. Coverage is 0.2x.
  Valuation:      4.0x EV to exit-rate revenue. Forward P/E 119x. TTM P/E undefined — no earnings.
  What changed:   Guidance up across every line; power target raised to 1.85 GW.
  What to watch:  Q3 operating profit against the $200–260M guide.
  The call:       [One sentence. Take a position, or say explicitly that you're not taking one.]
```

Rules:
- **Every line carries a number.** A TLDR without figures is a mood.
- **The catch line is mandatory.** If you cannot fill it, you have not finished the analysis.
- **The call line takes a position or declines out loud.** "Not enough information to have a
  view, and here is what would give me one" is a legitimate call. Vagueness is not.
- No new information. Everything in the TLDR appears earlier with a source.

---

## Failure modes

| Symptom | Cause |
|---------|-------|
| P/E quoted for a loss-making company | Adjusted EPS substituted without disclosure |
| PEG on a company with decelerating growth | Forward growth taken from a trailing rate |
| Rule of 40 quoted as a single number | Variant not named — check which margin was used |
| Margins look great, stock is falling | Cash conversion or interest coverage was skipped |
| "Record revenue" with no context | Run-rate or seasonality not addressed |
| Every metric is green | Provenance assigned at write-up time instead of at research time |
