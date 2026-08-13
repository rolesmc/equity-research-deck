# equity-research-deck

A [Claude](https://claude.ai/code) skill that researches a company, sector, or thesis and
renders the analysis as a presentation-grade single-file HTML deliverable.

Two output modes:

- **Deck** — keyboard-navigable slides for one company and one argument. Earnings
  breakdowns, valuation walkthroughs, thesis presentations.
- **Dashboard** — a scrolling institutional-research page for a sector or theme. Flow
  maps, scoreboards, tier rankings, monitoring systems.

Both produce a single `.html` file with no build step, no dependencies, and no server.
It opens in any browser, emails cleanly, and works offline.

---

## What it actually enforces

Most "make me a chart" prompts produce something that looks like research. This skill
encodes the conventions that make research trustworthy:

**Epistemic color coding.** Every number is typed by provenance at render time — green
for company-stated fact, amber for author estimate, red for risk. The legend ships on
slide 2. A reader can always tell what was filed from what was guessed.

**Enterprise value discipline.** Multiples are computed against market cap *plus debt
minus cash*, not market cap. A company with $35B of debt is not priced at its equity value.

**The unit economic.** Every business scales on some denominator — revenue per gigawatt,
per store, per subscriber. The skill finds it, sanity-checks it two independent ways, and
puts it on a slider so the reader can move it and watch the conclusion change.

**A real bear case and explicit kill criteria.** Not a token risks slide. The specific,
falsifiable conditions under which the thesis is wrong.

**Disclosure.** Positions held, as-of dates, and "not financial advice" are enforced by
the validator, not left to memory.

---

## Install

Clone into your Claude skills directory:

```bash
git clone https://github.com/YOUR-USERNAME/equity-research-deck.git ~/.claude/skills/equity-research-deck
```

Or, for a single project, drop it in `.claude/skills/` inside the repo you're working in.

Verify Claude can see it by asking for the skill by name, or just make a request that
matches it:

> Build me a deck on NVDA's latest quarter
>
> Map the public ways to own the data-center power buildout

No dependencies. The validator needs Python 3.8+, which macOS and most Linux distros ship
by default.

---

## Usage

Point it at a subject:

```
Build a deck on CRWV's Q2 — focus on whether the debt load is sustainable
```

It will scope the question, research from primary sources, run the quantitative
breakdown, render the HTML, and validate the output. You get a file path back.

Check the result yourself:

```bash
python3 scripts/validate_deck.py my-deck.html
```

The validator checks structure — color coverage, source notes, disclosure block,
navigation integrity, accessibility basics. It cannot check whether your argument is
correct. Read the deck.

---

## Repo layout

```
equity-research-deck/
├── SKILL.md                        # Entry point — workflow and non-negotiables
├── references/
│   ├── research-protocol.md        # Source hierarchy, as-of dating, bear-case sourcing
│   ├── metrics-playbook.md         # EV, unit economics, sensitivity, multiples
│   ├── deck-architecture.md        # The 11-slide arc and the 7-section dashboard arc
│   ├── design-system.md            # Tokens, type, components, Artifact-CSP notes
│   └── epistemic-standards.md      # Fact vs. estimate, kill criteria, disclosure
├── assets/
│   ├── deck-template.html          # Working deck — nav, dots, dial, reveal
│   ├── dashboard-template.html     # Working dashboard — ticker, flow map, scoreboard
│   └── example-brief.md            # Worked input → output contract
└── scripts/
    └── validate_deck.py            # Standard-library QA pass
```

Both templates render standalone with placeholder content — open them before you write
anything to see what you're filling in.

---

## Design notes

The visual identity is dark-only and deliberately so. Both source deliverables commit to
it, and a light theme would dilute the house style rather than serve it.

Templates load Archivo, Inter, and JetBrains Mono from Google Fonts with a documented
fallback stack. If you are rendering into a Claude Artifact, its content-security policy
blocks font CDNs — `references/design-system.md` gives the system-font substitution that
keeps the same proportions.

---

## Limitations

- It fetches from public sources at runtime. It ships no market data and has no data
  feed; figures are only as fresh as the session that produced them.
- It is not a recommendation engine. It produces research documents with enforced
  disclosure, not advice.
- The validator checks form, not substance. It will happily pass a beautifully formatted
  wrong answer.

## License

MIT — see [LICENSE](LICENSE).
