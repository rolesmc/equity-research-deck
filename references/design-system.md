# Design System

Dark-only, terminal-adjacent, built for a financial reader. The identity is deliberate:
the deliverable should look like something from a trading desk, not a marketing team.

---

## Tokens

### Deck palette (`assets/deck-template.html`)

```css
:root{
  --bg:#070A0F;      /* near-black, blue-biased */
  --panel:#0D131B;   /* card ground */
  --panel2:#111925;  /* nested card */
  --line:#1A2431;    /* borders */
  --ink:#E8EFF6;     /* primary text */
  --dim:#7C90A6;     /* secondary text */
  --faint:#4A5D71;   /* labels, metadata */

  --fact:#35D69A;    /* company-stated — green */
  --est:#F2B33D;     /* author estimate — amber */
  --risk:#E8695E;    /* risk / downside — red */
}
```

### Dashboard palette (`assets/dashboard-template.html`)

Two accent families instead of one, because the dashboard's job is to separate two
*categories* of asset, not two categories of certainty:

```css
:root{
  --bg:#0A0C10; --bg2:#0E1117; --surface:#141A22; --surface2:#1A222C;
  --line:#242D39; --line2:#333E4D;
  --text:#EAE8E2; --muted:#8B94A3; --muted2:#5A6473;

  --copper:#C87B4A; --copper-br:#E39A63; --copper-dim:#7A5334;  /* the supply chain */
  --teal:#35B8A6;   --teal-br:#54D8C4;   --teal-dim:#1E5F57;    /* the scarce asset */

  --green:#57D368; --red:#F0616D; --amber:#E3AC44;              /* semantic state */
}
```

The neutrals are hue-biased, not pure grey — the deck's toward blue, the dashboard's text
(`#EAE8E2`) slightly warm against a cool ground. Do not substitute `#888`.

**Semantic color is separate from accent color.** Green/red/amber mean fact/risk/estimate
and up/down. Teal and copper mean category. Never let them collide.

---

## Type

Three roles, always. The pairing is what makes the format read as a research document.

| Role | Deck | Dashboard | Used for |
|------|------|-----------|----------|
| Display | Archivo 700/800 | Archivo 800/900 | Headlines, card titles |
| Body | Inter 400/500/600 | Inter 400/500/600 | Prose |
| Mono | JetBrains Mono 400/500/700 | IBM Plex Mono 400/500/600 | **Every number**, labels, eyebrows |

```html
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

### Rules

- **All numeric content is mono.** Table cells, KPI values, dial outputs, tickers. This is
  what makes columns align and what makes the document read as data.
- Display face gets negative tracking: `letter-spacing:-.02em` to `-.035em` at large sizes.
- Mono labels get positive tracking: `letter-spacing:1.8px–3px`, uppercase, 9–11px.
- Body prose caps at `max-width:70ch`.
- Fluid sizing throughout: `font-size:clamp(38px,7.4vw,86px)` for h1.

### Rendering into a Claude Artifact

The Artifact CSP blocks font CDNs — a `<link>` to Google Fonts fails silently and you get
a fallback you did not choose. Substitute, keeping the same three roles:

```css
--disp: "Archivo","Helvetica Neue",Helvetica,Arial,sans-serif;
--body: "Inter","Segoe UI",Roboto,system-ui,sans-serif;
--mono: "SF Mono",ui-monospace,Menlo,Consolas,monospace;
```

Proportions hold; the character is softer. For standalone HTML files — the default output —
keep the CDN link.

---

## Components

### KPI tile

Left border carries the semantic type. Four per row, `minmax(160px,1fr)`.

```html
<div class="kpi risk">
  <div class="l">Interest paid</div>
  <div class="v risk">$640M</div>
  <div class="n">The problem</div>
</div>
```

`.l` mono 9px uppercase faint · `.v` mono 700 clamp(22px,3.3vw,32px) · `.n` 12px dim.

### Data table

Right-aligned numerics, left-aligned first column, mono everywhere except the label column.
`tr.hi` highlights the row that carries the argument.

```html
<table>
  <tr><th>Measure</th><th>Amount</th><th>Multiple of $76B</th></tr>
  <tr><td>2026 revenue</td><td>$12.8B</td><td>~6.0x</td></tr>
  <tr class="hi"><td>Revenue rate exiting 2026</td><td>$19.0B</td><td class="fact">~4.0x</td></tr>
</table>
```

Wrap in `.tblscroll { overflow-x:auto }` — the page body must never scroll sideways.

### Caveat note

The fair-play block. Panel ground, no accent border, sits directly under the chart it
qualifies.

```html
<div class="note">
  <h4>Be fair about this</h4>
  <p>Profit is better than <em>last quarter</em>, not better than <em>last year</em>.</p>
</div>
```

### Quote + translation

```html
<div class="quote">
  <p>The deployment delivers attractive returns, fully repaying asset-level debt…</p>
  <cite>NITIN AGRAWAL, CFO</cite>
</div>
<p><b>In plain terms:</b> each batch of chips pays off its own loan…</p>
```

Left border in `--fact`, italic body, mono cite. **Always followed by the translation.**

### Bar chart

CSS-only, animates on slide activation via `--h` custom property. No chart library.

```html
<div class="cb now"><div class="val fact">$128M</div>
  <div class="col" style="--h:50%"></div><div class="lab">Q2'26</div></div>
```

`.now` fills with `--fact`, `.low` with a muted tone. Heights are percentages of the tallest
bar — compute them, do not eyeball them.

### Ramp ladder

Year label, track, amount. `.rung.est` switches the fill to amber for interpolated years.

```html
<div class="rung"><span class="yr">2026</span>
  <span class="track"><span class="fill" style="--w:23%"></span></span>
  <span class="amt fact">1.85 GW</span></div>
<div class="rung est"><span class="yr">2027</span>
  <span class="track"><span class="fill" style="--w:38%"></span></span>
  <span class="amt est">~3 GW</span></div>
```

### Sensitivity dial

A `<input type="range">` with a live-computed output grid and a zone label. Full mechanics
in `references/metrics-playbook.md` §3. Two requirements: `aria-label` on the input, and
the keyboard handler must skip arrow-key slide navigation when the range is focused —
already handled in the template:

```js
if (e.target.type === 'range') return;
```

### Risk card

`.rk` red left border, `.rk.mid` amber, `.rk.lo` faint. Numbered in the heading, ranked by
severity.

### Verdict chip (dashboard)

Ticker + purpose tag + verdict dot, in a stage column of the flow map.

```html
<span class="chip firm"><span class="vd buy"></span><b>CEG</b><span class="tag">largest fleet</span></span>
```

---

## Motion

Restrained and functional. Motion exists to direct attention on slide entry, not to decorate.

- **Slide reveal** — children of `[data-on="1"]` fade up 12px, staggered 60ms, capped at 6.
- **Chart grow** — bars and fills animate from 0 on activation, `cubic-bezier(.2,.8,.3,1)`,
  ~0.8s, staggered 60–80ms.
- **Progress bar** — width transition, 0.45s.
- Nothing loops. Nothing bounces. No parallax.

Reduced motion is mandatory and must leave content in its final state:

```css
@media (prefers-reduced-motion:reduce){
  *{transition:none!important;animation:none!important}
  .r{opacity:1;transform:none}
  .cb .col{height:var(--h)} .rung .fill{width:var(--w)}
}
```

Note the last line — disabling the transition without restoring the final height leaves
every bar at zero. This is the bug to check for.

---

## Accessibility

- Every interactive control has a visible `:focus-visible` outline in `--fact`.
- Dots are real `<button>` elements with `aria-label` and `aria-current`.
- Nav buttons carry `aria-label`; disabled state is `[disabled]`, not opacity alone.
- The range input has an `aria-label` naming units.
- Never encode meaning in color alone. Green numbers also appear in a legend; verdict dots
  are paired with text labels; risk severity is stated in the heading, not just the border.
- Contrast: `--dim` on `--bg` clears 4.5:1. `--faint` is for 9–11px uppercase labels only —
  do not use it for body prose.

---

## Responsive

- Deck: fixed 52px header / 54px footer, slides absolutely positioned between, each
  independently scrollable with `overscroll-behavior:contain`.
- Dashboard: `max-width:1240px`, flow map collapses to a single column under 1000px with
  arrows rotated 90°.
- Touch: horizontal swipe advances the deck, 60px threshold, `{passive:true}`.
- Every wide table gets its own `overflow-x:auto` container.
- Test at 375px. The KPI grid, flow map, and conviction rows all have explicit breakpoints.
