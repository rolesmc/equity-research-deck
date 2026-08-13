# Epistemic Standards

What separates a research document from a pitch. These are the rules that survive contact
with a skeptical reader.

---

## The three types

Every number in the deliverable is exactly one of these. Decide at research time, not at
render time.

### Fact — `--fact`, green

A figure a company stated, a regulator published, or a filing contains. The test: **can you
point at the document and the page?**

Includes: reported revenue, guidance ranges, contracted backlog, fund AUM and fee, holdings
weights, announced policy figures, direct management statements.

Guidance is a fact — it is a fact *about what management said*, not about the future.
Present it as such: "Management guides $200–260M next quarter."

### Estimate — `--est`, amber

Anything you computed, interpolated, or judged. The test: **would a careful reader with the
same sources get a different number?** If yes, it is amber.

Includes: derived unit economics, interpolated ramp years, thematic purity percentages,
implied multiples on your own forecasts, scoring weights, any "~" figure.

Estimates are rounded. `~$10B per gigawatt`, not `$10.27B`. Precision on a guess is a tell.

### Risk — `--risk`, red

Not a separate provenance — an overlay. A number is red when it represents downside, a
widening gap, or a threshold being crossed. Interest expense of $640M is a company-stated
fact *and* the problem; it renders red because its role in the argument is the risk.

---

## Interpolation must be visible

When you fill years between two guided anchors, the anchors are green and the fill is
amber, and the body text says so:

> Here's the ramp — green is what the company has stated, amber is my own interpolation
> between their two anchors.

| Year | Value | Type |
|------|-------|------|
| 2026 | 1.85 GW | fact — company guidance |
| 2027 | ~3 GW | estimate — interpolated |
| 2028 | ~4.5 GW | estimate — interpolated |
| 2029 | ~6.2 GW | estimate — interpolated |
| 2030 | 8 GW+ | fact — company stated |

Never present a smooth curve that implies five data points when you have two.

---

## Be fair about your own chart

The single highest-leverage credibility move in the format. Wherever a chart or figure
flatters the argument, the caveat goes directly beneath it — not in an appendix.

> **Be fair about this.** Profit is better than *last quarter*, not better than *last year*.
> Operating margin is 5% today versus 16% a year ago. What changed is the direction, not
> the level. Anyone calling this the most profitable quarter ever is misreading the chart.

The pattern: state the flattering reading, state the unflattering one, name which is true,
and explicitly correct the overenthusiastic version of your own case.

Common places this is required:

| Situation | The correction owed |
|-----------|--------------------|
| Sequential improvement off a low base | Compare to prior year too |
| Trailing Sharpe or return in a bull run | Say the period describes the market, not an edge |
| A multiple that looks cheap on exit-rate revenue | Show the current-year multiple as well |
| Growth in a small-base segment | Give the absolute dollars |
| A metric that changed definition | Say when, and show both bases |

---

## The bear case is a section, not a bullet

Three-part structure:

1. **State the objection in its strongest form**, in its own voice. Not a caricature.
   "The chips go worthless in two years" is the headline of the reference deck's bear slide.
2. **Present the answer**, quoted from management if they have addressed it, with the
   translation into plain English.
3. **Say whether you buy it.** Quoting the CFO is evidence, not analysis. The deck has to
   take a position.

If you cannot find a credible bear case, you have not researched enough. There is always
one.

---

## Kill criteria

Explicit, falsifiable conditions under which the thesis is wrong. Written before the
outcome is known, so the reader can hold you to them.

Not kill criteria: "if the stock falls." Price is not evidence.

Kill criteria look like:

- Q4 operating margin comes in under 8% against low-teens guidance
- The chip-life depreciation assumption is shortened below six years
- A new debt facility closes materially smaller than announced, or is pulled
- Revenue per gigawatt declines two quarters running
- The fund fails to gather assets past $350M through 2027 — closure risk

Each is specific, observable, and dated. Pair them with the monitoring table so the reader
knows both what to watch and what the reading would mean.

---

## Where this could be wrong

A separate obligation from the bear case. The bear case is the market's objection to the
*subject*; this is your objection to your *own analysis*.

> Two honest counterarguments. First, if quantum commercializes faster than consensus,
> QTUM's 20% pure-play weight means the core leg badly underperforms the theme it is meant
> to express. Second, WQTM's sub-$350M asset base carries genuine closure risk.

Two is usually right. One reads as a formality; four reads as no conviction.

---

## Disclosure

Every deliverable ends with, in plain language:

- **Not advice.** "Education only — not advice, not a recommendation. I'm not a registered
  investment adviser."
- **Positions held.** If the author holds the security, say so and call it a conflict.
  `<span class="pill">AUTHOR HOLDS CRWV</span>`
- **Data vintage.** "Figures come from the Q2 2026 earnings release, investor deck and call
  transcript dated August 11, 2026."
- **Verification pointer.** "Market cap and debt are approximate — verify against the 10-Q."
- **Estimate flag.** "Anything marked amber is my own estimate, not company guidance, and
  will be wrong to some degree."

The validator checks for a disclosure block. It cannot check that it is honest.

---

## Language discipline

| Do | Don't |
|----|-------|
| "Management guides $200–260M" | "The company will earn $200–260M" |
| "Roughly eight years of work is already booked" | "Incredible backlog" |
| "That reads conservative, not neutral" | "Analysts are wrong" |
| "This is a bet on firm power scarcity" | "This is a can't-miss opportunity" |
| "The last ~2 GW is the genuinely uncertain part" | Silence about the uncertain part |

No superlatives you cannot source. No "poised to," "set to soar," "hidden gem." If the
argument needs adjectives, the numbers are not doing the work.
