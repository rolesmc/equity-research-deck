# Research Protocol

Research happens before a template is opened. A deck built while researching becomes a
deck shaped by whatever was found first.

---

## 1. Write the one-paragraph version first

Before any searching, write the thesis in one paragraph a non-specialist could follow.
If you cannot, you do not understand the subject yet — that is the signal to keep reading,
not to start building.

This paragraph becomes slide 2 of the deck almost verbatim. From the reference deck:

> CoreWeave rents out AI computing power. Customers have already signed $104 billion of
> contracts. The company will do about $13 billion of revenue this year — so roughly eight
> years of work is already booked. The whole business costs about $48 billion. The catch is
> debt: CoreWeave borrows heavily to build data centers, and interest payments are growing fast.

Four sentences: what it does, the scale of demand, the price, the catch. No jargon, no
adjectives, one number per sentence.

---

## 2. Source hierarchy

Work top-down. Do not use a lower tier for something a higher tier answers.

| Tier | Source | Use for |
|------|--------|---------|
| 1 | Earnings release, 8-K, investor deck | Reported figures, guidance |
| 1 | 10-Q / 10-K | Balance sheet, debt, share count, accounting policy |
| 1 | Call transcript | Management's own framing, direct answers to the bear case |
| 1 | Fund fact sheet / prospectus | ETF holdings, fees, index methodology |
| 2 | Exchange and fund data aggregators | Returns, AUM, ratios, betas |
| 2 | Regulator and agency releases | Policy catalysts, funding announcements |
| 3 | Sell-side notes, financial press | The consensus view — mainly so you can locate yourself against it |
| 3 | Independent analysts, forums | The bear case you would otherwise miss |

**Tier 3 is for arguments, not for numbers.** If a figure only exists in tier 3, either
find it in a filing or mark it amber.

---

## 3. Record every figure with provenance

Keep a running table while you research. Not optional — this table becomes the source
notes in the output.

| Figure | Value | Source | As-of | Type |
|--------|-------|--------|-------|------|
| Signed contracts | $104B | Q2'26 earnings release | 11 Aug 2026 | fact |
| Revenue per GW | ~$10.3B | Derived: $19.0B guide ÷ 1.85 GW | 11 Aug 2026 | estimate |
| 2030 power | 8 GW+ | Management, "a floor not a target" | 11 Aug 2026 | fact |
| 2028 power | ~4.5 GW | Interpolated between 2026 and 2030 anchors | — | estimate |

The **Type** column is what drives the color class in the output. Fill it as you go; do
not try to reconstruct provenance later.

### The as-of date rule

A figure without an as-of date is unusable. Market caps, prices, AUM, and yields move.
State the date once prominently (the eyebrow line) and again in the source notes.

Where sources disagree — and they will, on AUM and market cap especially — **use the more
conservative figure and disclose the range.** The reference analysis quoted QTUM AUM at
"$5.22B–$5.6B across sources" and used the lower number throughout.

---

## 4. Hunt the bear case deliberately

The failure mode is building a deck that only surveys agreeable sources. Spend real time
here.

**Find the loudest specific objection.** Not "it's expensive" — the actual mechanical
argument. For AI infrastructure it is chip depreciation schedules. For pre-revenue tech
it is dilution. For a thematic ETF it is that the fund does not hold what its name implies.

**Find management's answer to it.** Call transcripts are where this lives. If management
has addressed the objection directly, quote them and then translate:

> **In plain terms:** each batch of chips pays off its own loan and turns a profit during
> the first contract. Anything it earns after that is free money.

**Then say whether you believe them.** Quoting the CFO is not analysis. The deck must take
a position on whether the answer is adequate.

**Check whether the bear case has already happened.** Look at the actual series — margins,
interest expense, share count — over five or more periods. A trend beats an argument.

---

## 5. Establish the comparison set

A number alone means nothing. Every headline figure needs one of:

- **A time comparison** — same metric, prior period and prior year. Both, because they
  can point in opposite directions and that gap is usually the story.
- **A peer comparison** — the same metric for two or three genuine comparables.
- **A benchmark** — the index, the sector average, the risk-free rate.

For funds specifically: fee, AUM, holdings count, top-10 concentration, and inception date
for every fund in the set, or the comparison is not honest.

---

## 6. Sufficiency check

Do not proceed to the build until all of these are true:

- [ ] The one-paragraph thesis is written and survives reading it aloud.
- [ ] Every headline figure has a tier-1 source and an as-of date.
- [ ] Every derived figure has its arithmetic written down and is marked estimate.
- [ ] The strongest opposing argument is identified, sourced, and answered — or conceded.
- [ ] At least five periods of history exist for the metric the thesis turns on.
- [ ] The single driving variable for the sensitivity model is identified.
- [ ] Kill criteria are written: the specific conditions that would make you wrong.

If a box is unchecked, the deck built on it will have a hole in exactly that place.
