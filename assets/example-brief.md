# Worked Example

The input → output contract, end to end. This is the shape of a good run.

---

## Input

> Build a deck on CoreWeave's Q2 — I want to know whether the debt load is sustainable.

Everything below was derived from that one line.

---

## Step 1 — Scope

| | |
|---|---|
| **Subject** | CoreWeave (NASDAQ: CRWV), Q2 2026 |
| **Question** | Can they keep financing the build? |
| **Audience** | Retail-adjacent, understands "revenue" and "debt", not "asset-level leverage" |
| **Mode** | Deck — one company, one linear argument |

The user's framing ("whether the debt load is sustainable") *is* the question. Don't
replace it with a generic earnings recap.

## Step 2 — One paragraph, written before searching

> CoreWeave rents out AI computing power. Customers have already signed $104 billion of
> contracts. The company will do about $13 billion of revenue this year — so roughly eight
> years of work is already booked. The whole business costs about $48 billion. The catch is
> debt: CoreWeave borrows heavily to build data centers, and interest payments are growing fast.

Four sentences, one number each, no jargon. This becomes slide 2.

## Step 3 — Source table (excerpt)

| Figure | Value | Source | As-of | Type |
|--------|-------|--------|-------|------|
| Revenue | $2.58B | Q2'26 earnings release | 11 Aug 2026 | fact |
| Signed contracts | $104B | Q2'26 earnings release | 11 Aug 2026 | fact |
| Operating profit | $128M | Q2'26 earnings release | 11 Aug 2026 | fact |
| Interest expense | $640M | Q2'26 earnings release | 11 Aug 2026 | fact → **risk** |
| Interest guide, Q3 | $860–940M | Management guidance | 11 Aug 2026 | fact → **risk** |
| Total debt | ~$35B | 10-Q balance sheet | 30 Jun 2026 | fact |
| Cash | $6.9B | 10-Q balance sheet | 30 Jun 2026 | fact |
| **Enterprise value** | **~$76B** | Derived: 48 + 35 − 6.9 | 11 Aug 2026 | estimate |
| Revenue per GW | ~$10.3B | Derived: $19.0B ÷ 1.85 GW | 11 Aug 2026 | estimate |
| 2027–29 power | ~3 / ~4.5 / ~6.2 GW | Interpolated between anchors | — | estimate |
| 2030 power | 8 GW+ | Management, "a floor not a target" | 11 Aug 2026 | fact |

Interest expense is a company-stated **fact** that renders **red**, because its role in
the argument is the risk. Provenance and role are different axes.

## Step 4 — The technical breakdown

**Enterprise value.** $48B market cap + $35B debt − $6.9B cash = **~$76B**. Using market
cap here would understate the price of the business by 37%.

**The unit economic**, sanity-checked twice:

| Check | Revenue | Power | Per GW / yr |
|-------|---------|-------|-------------|
| Q2 annualized | $10.3B | ~1.15 GW | ~$9.0B |
| Company's year-end target | $19.0B | 1.85 GW | ~$10.3B |

Two independent paths bracket it at $9–10B per GW. The spread points up, which supports
the bull case — and the July price increase is not yet in either number.

**The dial.** Driver: revenue per GW. Range $8.0–15.0B. Default $10.3B. Outputs: 2030
revenue at 8 GW, growth multiple vs. today, implied CAGR, EV/2030 revenue.

**The gap that is the whole story.** Interest $267M → $536M → $640M → ~$900M guided,
against ~$230M of operating profit. Widening. Two series, one chart.

## Step 5 — The bear case

**Objection:** "The chips go worthless in two years." AI infrastructure depreciation
schedules are too long, so reported earnings are overstated.

**Answer:** The CFO addressed it directly — an A100 from 2020 was just contracted through
2029, and asset-level debt is repaid within the first contract.

**Translation:** each batch of chips pays off its own loan and turns a profit during the
first contract. Anything after is incremental.

**Verdict:** the answer is adequate *for chips already deployed*. It says nothing about
whether the next $35B of capex clears the same bar. Say that.

## Step 6 — Kill criteria

- Q4 operating margin under 8% against low-teens guidance
- Depreciation life shortened below six years
- A debt facility closes materially smaller than announced, or is pulled
- Revenue per GW declines two quarters running

## Step 7 — Build and validate

```bash
cp assets/deck-template.html output/crwv-q2-2026.html
# fill every [BRACKET]
python3 scripts/validate_deck.py output/crwv-q2-2026.html
```

Expected clean result:

```
validate_deck — crwv-q2-2026.html
  mode: deck  ·  slides: 11  ·  tables: 4

  PASS — no structural issues found.

  Structure is not substance. Read the deck.
```

---

## What a weak run looks like

| Symptom | What went wrong |
|---------|-----------------|
| Every number is green | Provenance was assigned at render time, not research time |
| The bear-case slide lists generic risks | No transcript was read |
| Multiples computed on market cap | EV discipline skipped — the valuation slide is wrong |
| The ramp is a smooth five-point curve | Two anchors were presented as five data points |
| No "be fair about this" note anywhere | The deck is arguing, not analyzing |
| Validator passes, deck is unreadable | Structure is not substance — read it yourself |
