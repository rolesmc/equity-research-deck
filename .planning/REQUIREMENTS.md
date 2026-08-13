# REQUIREMENTS

| ID | Requirement | Phase |
|----|-------------|-------|
| REQ-01 | Repo is GitHub-ready: README, MIT LICENSE, .gitignore, install instructions | 01 |
| REQ-02 | `SKILL.md` has valid frontmatter (name, description) and triggers on deck/research requests | 01 |
| REQ-03 | Skill defines a research protocol that runs *before* any template is opened | 02 |
| REQ-04 | Epistemic color system (fact / estimate / risk) is documented and enforced | 02 |
| REQ-05 | Metrics playbook covers EV discipline, unit economics, single-driver sensitivity, multiples | 02 |
| REQ-06 | Design system documents palette, type, components, and the Artifact-CSP font caveat | 02 |
| REQ-07 | Deck architecture spec defines the canonical 11-slide arc and the dashboard section arc | 02 |
| REQ-08 | `assets/deck-template.html` renders standalone: keyboard nav, dots, progress bar, reveal, dial | 03 |
| REQ-09 | `assets/dashboard-template.html` renders standalone: ticker, nav, flow map, scoreboard, tiers | 03 |
| REQ-10 | Both templates are single-file, no build step, keyboard accessible, reduced-motion safe | 03 |
| REQ-11 | `scripts/validate_deck.py` checks color coverage, sources, disclosure, nav integrity | 04 |
| REQ-12 | Validator is standard-library only (no pip install) and exits non-zero on failure | 04 |
| REQ-13 | A worked example brief shows the expected input → output contract | 05 |
| REQ-14 | Every template verified to open and function before repo is declared done | 05 |

## Decisions (CONTEXT)

- **D-01** Single-file HTML output. No React, no bundler — the deliverable must survive
  being emailed, dropped in Discord, or opened offline.
- **D-02** Google Fonts via CDN in the templates, with a documented fallback stack.
  Noted caveat: Claude Artifacts' CSP blocks font CDNs, so the design doc gives the
  system-font substitution for that target.
- **D-03** Two templates, not one configurable one. The deck and the dashboard have
  genuinely different information architecture; merging them would produce a worse both.
- **D-04** Python validator over a Node linter — Python 3 is present on macOS by default,
  Node is not (confirmed on this machine).
- **D-05** Dark-only visual identity. Both references commit to it; a light theme would
  dilute the house style rather than serve it.
