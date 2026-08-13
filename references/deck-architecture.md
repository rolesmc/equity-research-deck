# Deck Architecture

The information architecture for both output modes. These arcs are derived from working
deliverables; deviate when the subject demands it, but know what you are giving up.

---

## Mode A — The Deck (one company, one argument)

Eleven slides. Each answers one question. If a slide does not answer a question, cut it.

| # | Slide | Question it answers | Required elements |
|---|-------|--------------------|-------------------|
| 01 | **Title** | What is this and how current is it? | Headline stating the finding (not the topic), 3–4 metadata tiles, as-of date, nav hint |
| 02 | **The short version** | What if I read nothing else? | The one-paragraph thesis, the "what are you actually betting on" note, **the color legend** |
| 03 | **The quarter / the setup** | What was reported? | 4 KPI tiles, "three things worth knowing" |
| 04 | **The turn** | What changed, and is it real? | 5-period bar chart, a "be fair about this" caveat note |
| 05 | **Guidance** | What does management expect? | Was/Now table, one plain-English explainer of the key unit |
| 06 | **The bear case** | What is the strongest objection? | The objection stated in its own words, management's answer quoted, your translation |
| 07 | **The engine** | What drives the long-term model? | Multi-year ramp ladder, green anchors and amber interpolation |
| 08 | **The one variable** | What does everything reduce to? | Two independent sanity checks, then the interactive dial |
| 09 | **Valuation** | What do you pay today? | EV derivation, multiple table, where consensus sits and what it assumes |
| 10 | **What could go wrong** | How does this break? | 5–6 ranked risk cards, severity-colored, first one is the one that matters |
| 11 | **Bottom line** | So what? | The bet stated plainly, then a good/bad monitoring table, then disclosure |

### Structural rules

**Slide 2 carries the legend.** Introduce the color system before the first colored number
appears, not in a footnote at the end.

**Slide 4 must include the fair-play note.** Wherever the headline chart flatters the
argument, the caveat sits directly beneath it. This is the highest-leverage credibility
move in the format.

**Slide 10's first risk is the one everything else runs through.** In the reference deck:
"They run out of borrowing room… Every other risk runs through this one." Rank by
severity, and say which risk subsumes the others.

**Slide 11 ends with a checklist, not a conclusion.** A table of what-to-watch with
explicit good and bad thresholds turns the deck into something the reader uses next
quarter instead of reads once.

| Watch | Good | Bad |
|-------|------|-----|
| Q3 operating profit | $200–260M | Under $200M |
| Q4 operating margin | Low teens | Under 8% |
| Chip lifespan assumption | Stays 6 years | Gets shortened |

### One idea per slide

If a slide needs two headings, it is two slides. The reveal animation staggers children of
`[data-on="1"]` by ~60ms — that only reads well with 4–6 top-level blocks per slide.

---

## Mode B — The Dashboard (a sector, many names)

Seven sections, scrolling, with sticky navigation. Numbered because the sections are a
genuine argument sequence: thesis → map → data → price → example → verdict → monitoring.

| # | Section | Purpose | Signature element |
|---|---------|---------|-------------------|
| 01 | **The Thesis** | Establish the asymmetry the whole page rests on | Demand/supply chart + 6 fact tiles |
| 02 | **The Flow Map** | Show the value chain as stages, every stage a trade | Horizontal stage columns with verdict-dotted ticker chips |
| 03 | **The Scoreboard** | Every name on comparable forward numbers | Wide sortable table, tier-grouped, verdict badges |
| 04 | **Valuation Map** | What you pay vs. what you get | Multiple vs. growth positioning |
| 05 | **Featured Deep Dive** | One name examined properly | Price header, quad metrics, bull/bear cards, conviction bars |
| 06 | **The Verdict** | If I could own five | Tier cards: the five, add-on-weakness, yield, lottery tickets |
| 07 | **Monitoring** | What would change my mind | Catalyst calendar, leading indicators, kill criteria |

### Structural rules

**The hero states a differentiated call, not a topic.** "The AI buildout runs on
electrons" plus an explicit bet line: *"This is a bet on firm power scarcity — that
electrons, not GPUs, become the gating factor of the AI decade."*

**The flow map is the signature.** It converts a list of tickers into a causal structure.
Two color families: the scarce premium asset in the accent, the picks-and-shovels layer in
the secondary. Verdict dots (buy / watch / speculative) on each chip.

**The scoreboard needs tier headers,** not a flat sort. Grouping is analysis; sorting is
data.

**Section 07 is not optional.** Catalyst dates, leading indicators with pos/neg/neutral
state, and explicit kill criteria — the ✕-marked conditions that would end the thesis.

---

## Writing the copy

**Headlines state findings.** "CoreWeave finally turned growth into profit" — not
"CoreWeave Q2 2026 Results." "Demand is not the question. Supply is." — not "Market Overview."

**Define jargon inline, once.** *"'Power' is the unit of production here. Gigawatts of data
centers plugged in and running."*

**Translate every quote.** A CFO quote is evidence; the sentence after it is analysis.
Always follow with **In plain terms:**.

**Numbers belong in prose too.** "Next quarter's revenue guide implies roughly 158% growth
— accelerating, off a base that already doubled." The tile shows the number; the sentence
shows what it means.

**Concede in the deck's own voice.** "Anyone calling this the most profitable quarter ever
is misreading the chart." Correcting the overenthusiastic version of your own argument is
what separates research from promotion.

---

## Length discipline

| Mode | Target | Hard ceiling |
|------|--------|--------------|
| Deck | 11 slides | 14 — past that, split into two decks |
| Dashboard | 7 sections | 9 |
| Body text per slide | ≤ 70ch measure, 2–3 paragraphs | 4 |
| KPI tiles per row | 4 | 5 |
| Risk cards | 5–6 | 7 |
| Table rows before scroll | 12 | 20, then paginate or tier |
