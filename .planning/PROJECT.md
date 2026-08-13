# PROJECT — equity-research-deck

## Vision

A self-contained, GitHub-publishable Claude skill that takes a ticker, sector, or
thesis and produces a presentation-grade financial research deliverable: it does the
research, does the technical/quantitative breakdown, and renders the result as a
single-file HTML deck or dashboard.

The skill exists because the generic "make me a chart" path produces generic output.
This one encodes a specific house style derived from two reference deliverables the
author already built and shipped.

## What makes it different

1. **Epistemic color coding is mandatory, not decorative.** Every number is typed at
   render time as company-stated fact (green), author estimate (amber), or risk (red).
   The legend is on slide 2. A reader can always tell what is sourced from what is guessed.
2. **Research and presentation are one workflow, not two.** The skill runs a defined
   research protocol before it is allowed to open a template.
3. **The technical breakdown is the product.** Unit economics, EV-based multiples,
   a single-driver sensitivity model, and a bull/bear/kill-criteria structure.
4. **Two output modes**, matched to two jobs: a keyboard-navigable *deck* for a linear
   argument about one company, and a scrolling *dashboard* for a sector map with many names.

## Non-goals

- Not a data provider. It fetches from public sources at runtime; it ships no market data.
- Not a recommendation engine. Disclosure and "not financial advice" framing are enforced.
- No build step, no npm, no server. Output is one HTML file that opens in any browser.

## Success criteria

- A user clones the repo, drops it in `~/.claude/skills/`, types a ticker, and gets a
  deck with correct navigation, working sensitivity dial, and no unsourced green numbers.
- Templates render standalone with placeholder content before any research is done.
- The validator catches the four failure modes that actually happen: uncolored numbers,
  missing sources, missing disclosure, broken slide count.
