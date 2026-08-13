---
name: equity-research-deck
description: Research a company, sector, or thesis and render the analysis as a presentation-grade single-file HTML deck or dashboard. Use when the user asks for an equity research deck, earnings breakdown, sector map, investment thesis, stock analysis, valuation walkthrough, "slide deck" or "dashboard" about a ticker, ETF, or industry — or wants a financial overview presented visually rather than as prose. Also use when turning earnings results, 10-Q/10-K data, or market research into a shareable presentation.
---

# Equity Research Deck

Produces two kinds of deliverable, both single-file HTML that opens in any browser:

| Mode | Use when | Template |
|------|----------|----------|
| **Deck** | One company, one argument, delivered linearly. Earnings breakdowns, thesis walkthroughs, valuation cases. | `assets/deck-template.html` |
| **Dashboard** | A sector or theme with many names. Comparisons, scoreboards, supply-chain maps, screens. | `assets/dashboard-template.html` |

If the request names one ticker → deck. If it names a sector, theme, or "best X" → dashboard.
If genuinely ambiguous, ask once; don't guess and rebuild.

---

## The rule that matters most

**Every number is typed by where it came from.**

| Type | Color | Meaning | Class |
|------|-------|---------|-------|
| Fact | green `--fact` | Company-stated, filed, or reported. Traceable to a document. | `.fact` |
| Estimate | amber `--est` | Your calculation, interpolation, or judgment. | `.est` |
| Risk | red `--risk` | A number that represents downside, or a threshold being breached. | `.risk` |

The legend appears on slide 2 (deck) or in the flow legend (dashboard). It is not optional.
A reader must never have to guess whether `$104B` came from a press release or from you.

When you interpolate between two company-stated anchors — as in a multi-year ramp where
only the endpoints are guided — the interpolated rows are amber and the anchors are green.
Say so in the body text.

---

## Workflow

Run these in order. Do not open a template before step 4.

### 1. Scope

Establish, in one line each: the subject, the single question the deliverable answers,
and the audience's starting knowledge. Write the "one paragraph" version of the thesis
before doing anything else — if you cannot, you do not yet understand the subject well
enough to present it.

### 2. Research

Follow `references/research-protocol.md`. Minimum bar:
- Primary sources first (earnings release, investor deck, call transcript, 10-Q/10-K, fund fact sheet).
- Secondary sources only for context and for the bear case.
- Every figure recorded with its source and as-of date. Undated figures are unusable.
- Actively seek the strongest opposing argument. A deck without a credible bear case is marketing.

### 3. Analyze

Follow `references/metrics-playbook.md`. Required for a deck:
- Enterprise value, not market cap, for every multiple.
- The unit economic — revenue per gigawatt, per store, per subscriber, per rig. Find the
  denominator the business actually scales on.
- One driving variable isolated for the interactive sensitivity dial.
- Bull case, bear case, and explicit kill criteria.

### 4. Build

Copy the template, then fill it. Load `references/deck-architecture.md` for the slide arc
and `references/design-system.md` for components and tokens. Do not restructure the
navigation JavaScript — it is tested; content goes inside `.wrap`.

### 5. Validate

```bash
python3 scripts/validate_deck.py path/to/output.html
```

Fix everything it reports. Then open the file and click through it yourself — the
validator checks structure, not whether the argument holds.

---

## Non-negotiables

- **Disclosure.** Every deliverable ends with a plain-language disclaimer, any position
  the author holds, the as-of date of the data, and a "verify against the filing" note.
- **Sources with dates.** A figure without an as-of date is worthless three weeks later.
- **Be fair about your own chart.** Where a number flatters the argument, say what it
  omits. The reference decks do this explicitly ("Profit is better than *last quarter*,
  not better than *last year*") and it is the most credibility-building move available.
- **Plain English.** Define the jargon inline the first time. "Power is the unit of
  production here" beats assuming the reader knows.
- **No fabricated precision.** If you estimated it, it is amber and it is round.

## Reference files

Load on demand — not all at once.

| File | Load when |
|------|-----------|
| `references/research-protocol.md` | Starting research; deciding whether sourcing is sufficient |
| `references/metrics-playbook.md` | Doing the quantitative breakdown; building the sensitivity model |
| `references/deck-architecture.md` | Structuring slides or dashboard sections |
| `references/design-system.md` | Writing markup; choosing components; adapting for Artifacts |
| `references/epistemic-standards.md` | Deciding fact vs. estimate; writing the bear case and kill criteria |
