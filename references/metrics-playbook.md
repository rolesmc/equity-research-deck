# Metrics Playbook

The quantitative breakdown. This is the part that makes the deliverable research rather
than a summary.

---

## 1. Enterprise value, always

Market cap is the price of the equity. Enterprise value is the price of the business.

```
EV = market cap + total debt − cash & equivalents
```

Every multiple in the deck is computed against EV. State it explicitly, because most
readers have seen market-cap multiples and will otherwise assume that is what you mean:

> Market cap is ~$48B. But CoreWeave carries roughly $35B of debt against $6.9B of cash —
> so the true price of the business is closer to $76B. Always use that number.

For a capital-light business the two are close and it does not matter. For anything that
builds physical assets with borrowed money, using market cap understates the price by
half and the whole valuation section is wrong.

**Flag that EV moves.** If the company is actively borrowing to build, EV rises quarter
over quarter mechanically. Treat EV-based multiples as a shape, not a target.

---

## 2. Find the unit economic

Every business scales on a denominator. Find it, and the long-term model reduces to one
number.

| Business | Denominator | The metric |
|----------|-------------|-----------|
| Data-center / cloud infra | Gigawatts energized | Revenue per GW per year |
| Retail | Stores | Revenue per store, per square foot |
| Subscription software | Customers | ARPU, net revenue retention |
| Energy generation | Installed MW | Capacity factor, realized $/MWh |
| Semiconductors | Fab capacity | Revenue per wafer start |
| Fund / ETF | Assets | Fee revenue per $1B AUM |

### Sanity-check it two independent ways

One derivation is arithmetic. Two that agree is a finding. The reference deck did this:

| Check | Revenue | Power | Per GW / yr |
|-------|---------|-------|-------------|
| This quarter, annualized | $10.3B | ~1.15 GW | ~$9.0B |
| Company's own year-end target | $19.0B | 1.85 GW | ~$10.3B |

Two paths bracket the number at roughly $9–10B per GW. That bracket is more useful than
either point estimate, and the spread is itself information — here it says the metric is
improving, which supports the bull case.

If the two checks disagree by more than ~20%, do not average them. Find out why. The
reason is usually the finding.

---

## 3. The sensitivity dial

One slider, one variable, live-computed outputs. This is the single most valuable
interactive element in the deck and it earns its complexity.

**Pick the variable that everything reduces to.** Not revenue growth — that is an output.
The input: revenue per unit, take rate, margin at scale, terminal multiple.

**Compute at least three outputs from it,** so moving the slider shows the reader how the
conclusion is coupled:

```js
const TODAY = 12.8, EV = 76;                    // $B — state your constants
function draw(){
  const perUnit = sl.value / 10;                 // the driver
  const rev2030 = perUnit * 8;                   // × units at horizon
  mult.textContent = (rev2030 / TODAY).toFixed(1) + 'x';                  // growth multiple
  cagr.textContent = Math.round((Math.pow(rev2030/TODAY, 0.25)-1)*100)+'%'; // implied CAGR
  evx.textContent  = (EV / rev2030).toFixed(1) + 'x';                     // price paid today
}
```

**Label the zones.** A bare slider is a toy. Named ranges make it an argument:

| Range | Label |
|-------|-------|
| Below base | `BEAR — PRICING FALLS AS SUPPLY CATCHES UP` |
| At today's rate | `BASE CASE — TODAY'S RATE, HELD FLAT FOR FOUR YEARS` |
| Above base | `BULL — MIX SHIFTS TO INFERENCE AND SOFTWARE` |
| Far above | `AGGRESSIVE — SUSTAINED REAL PRICING GAINS` |

Color the zone label and the output values together — red, amber, green — so the epistemic
system extends into the interaction.

**Default the slider to the base case,** and say what the base case assumes. "Today's rate,
held flat for four years" is a disclosed assumption. A slider at an arbitrary position is not.

---

## 4. Multiples, stated against the right revenue

Show both current-year and exit-rate multiples. They differ enormously for anything growing
fast, and quoting only the flattering one is the most common sleight of hand in equity
research.

| Measure | Amount | Multiple of EV |
|---------|--------|----------------|
| Current-year revenue | $12.8B | ~6.0× |
| Revenue rate exiting the year | $19.0B | ~4.0× |

Then locate yourself against consensus, and say what consensus is implicitly assuming:

> Analysts are around $80B for 2030. That assumes revenue per gigawatt *does not improve at
> all* over four years — from a company that just raised prices 25% in a single month.
> That reads conservative, not neutral.

Naming the embedded assumption in the consensus number is worth more than the number.

---

## 5. Growth quality, not just growth

Decompose the headline. A revenue number that doubled tells you nothing about whether the
business is working.

- **Direction vs. level.** "Profit is better than *last quarter*, not better than *last
  year*. Operating margin is 5% today versus 16% a year ago. What changed is the direction,
  not the level." Say this when it is true. It costs you the headline and buys you the reader.
- **Five periods minimum** for any trend chart. Three points is a line you drew, not a trend.
- **The gap that matters.** Interest expense $267M → $536M → $640M → ~$900M guided, against
  ~$230M of operating profit. Two series on the same chart, one widening gap. That is a
  finding a table of levels would hide.

---

## 6. Fund and ETF analysis

Different discipline. For any thematic fund, the question is always: **does it hold what
its name implies?**

| Metric | Why |
|--------|-----|
| AUM | Below ~$100M, closure and spread risk are live |
| Expense ratio | Usually the least important differentiator; say so |
| Holdings count | Concentration proxy |
| **Top-10 weight** | The real concentration measure — read this before the name |
| **Thematic purity** | % of weight in companies whose *primary* business is the theme |
| Inception date | Under 12 months means no drawdown record exists |
| Index methodology | Equal-weight vs. cap-weight changes the risk profile entirely |

Purity is the finding that repays the work. A fund with "quantum" in its name holding 69%
in Micron, TSMC, NVIDIA and Broadcom is a semiconductor fund. Estimate purity from
published holdings and index methodology, mark it amber — it is your judgment, not a
disclosed figure.

**Discount trailing Sharpe ratios in a bull market.** A reading of 2–3 over a period in
which the theme tripled describes the period, not a durable edge. Say that out loud.

---

## 7. Scoring frameworks

When ranking several names or funds, publish the weights. An unweighted ranking is an
opinion wearing a table's clothes.

| Criterion | Weight | A | B | C |
|-----------|--------|---|---|---|
| Thematic purity | 25% | 3 | 5 | 1 |
| Diversification | 25% | 5 | 3 | 2 |
| Liquidity & scale | 20% | 5 | 2 | 2 |
| Track record | 20% | 5 | 1 | 1 |
| Cost | 10% | 5 | 4 | 3 |
| **Weighted** | | **4.50** | **3.05** | **1.60** |

State the weights are a judgment call for a specific investor profile, so a reader who
disagrees can re-weight rather than dismiss.

---

## 8. Arithmetic hygiene

- Show the derivation for anything computed. "EV of ~$76B divided by that 2030 revenue."
- Round estimates. `~$10B per gigawatt` — not `$10.27B`. False precision on an estimate
  is a tell.
- Keep facts precise. A reported figure is `$2.58B`, not `~$2.6B`.
- Use tabular figures (`font-variant-numeric: tabular-nums`) anywhere digits stack.
- State units in the header, not on every cell.
- Percentage change vs. percentage point change — never conflate them.
