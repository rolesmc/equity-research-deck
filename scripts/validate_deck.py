#!/usr/bin/env python3
"""Structural QA for equity-research-deck output.

Checks the four things that actually go wrong: numbers rendered without an
epistemic color class, missing source/disclosure blocks, broken navigation,
and unfilled template placeholders.

It validates form, not substance. A beautifully formatted wrong answer passes.

Usage:
    python3 scripts/validate_deck.py output.html
    python3 scripts/validate_deck.py output.html --strict   # warnings fail too

Standard library only. Exits 1 on any error.
"""

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# ---------------------------------------------------------------- constants

EPISTEMIC_CLASSES = {"fact", "est", "risk"}
# `dim` is an accepted neutral typing: prior-period or superseded figures that
# are deliberately not being claimed as current fact.
ACCEPTED_TYPINGS = EPISTEMIC_CLASSES | {"dim", "g-hi", "g-md", "g-lo", "up", "dn"}

# Numbers are only required to carry a typing when they sit in a *display slot* —
# a KPI value, a table cell, a dial output, a ramp amount. Figures inside prose
# are carried by the surrounding sentence and are not flagged.
DISPLAY_SLOT_CLASSES = {"v", "amt", "dval", "val", "n", "tn"}
DISPLAY_SLOT_TAGS = {"td"}

# A "significant" number: currency, percentage, multiple, or a magnitude-suffixed
# figure. Deliberately excludes bare small integers, which are usually list
# numbering or years in prose.
NUMERIC_RE = re.compile(
    r"""(?<![\w.])
    (?:
        \$\s?\d[\d,]*(?:\.\d+)?\s?(?:[KMBT]|bn|billion|million|trillion)?\b
      | \d[\d,]*(?:\.\d+)?\s?%
      | \d[\d,]*(?:\.\d+)?\s?[xX]\b
      | \d[\d,]*(?:\.\d+)?\s?(?:GW|MW|TWh|GWh|bps)\b
    )""",
    re.VERBOSE,
)

PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Za-z0-9 ./&'’,%+\-–—:$]{1,60}\]")

DISCLOSURE_MARKERS = (
    "not financial advice",
    "not advice",
    "not investment advice",
    "do your own research",
    "investment adviser",
    "investment advisor",
)

SOURCE_MARKERS = ("source", "figures come from", "as of", "verify against")

# Elements whose numeric content is chrome, not analysis.
SKIP_TAGS = {"script", "style", "title", "head", "nav", "cite"}
# Classes that legitimately carry uncolored numbers.
SKIP_CLASSES = {
    "count", "brand", "hint", "ticks", "lab", "yr", "dlab", "l",
    "srcnote", "tblfoot", "disc", "src", "cs", "co", "tag", "rt",
    "sec-tag", "eyebrow", "dt", "cl", "cv", "why", "gap",
}


class Finding:
    __slots__ = ("level", "code", "message", "context")

    def __init__(self, level, code, message, context=""):
        self.level = level
        self.code = code
        self.message = message
        self.context = context

    def render(self):
        mark = "ERROR" if self.level == "error" else "WARN "
        line = "  [{}] {}: {}".format(mark, self.code, self.message)
        if self.context:
            line += "\n           " + self.context
        return line


# ---------------------------------------------------------------- parsing


class DeckParser(HTMLParser):
    """Collects text nodes with their enclosing tag/class context."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []           # list of (tag, classes:set)
        self.text_nodes = []      # (text, tag, classes, colored: bool)
        self.slides = 0
        self.sections = 0
        self.range_inputs = []    # list of attr dicts
        self.buttons = []
        self.has_legend = False
        self.tables = 0
        self.scroll_wrapped_tables = 0
        self._table_depth_scroll = []

    # -- helpers

    def _classes(self, attrs):
        d = dict(attrs)
        return set((d.get("class") or "").split()), d

    def _active_classes(self):
        out = set()
        for _, cls in self.stack:
            out |= cls
        return out

    # -- handlers

    def handle_starttag(self, tag, attrs):
        classes, d = self._classes(attrs)

        if tag == "section":
            if "slide" in classes:
                self.slides += 1
            elif d.get("id"):
                self.sections += 1
        if tag == "input" and d.get("type") == "range":
            self.range_inputs.append(d)
        if tag == "button":
            self.buttons.append(d)
        if "legend" in classes or "flowlegend" in classes:
            self.has_legend = True
        if tag == "table":
            self.tables += 1
            enclosing = self._active_classes()
            if "tblscroll" in enclosing or "tblwrap" in enclosing:
                self.scroll_wrapped_tables += 1

        if tag not in ("br", "img", "input", "link", "meta", "hr"):
            self.stack.append((tag, classes))

    def handle_startendtag(self, tag, attrs):
        classes, d = self._classes(attrs)
        if tag == "input" and d.get("type") == "range":
            self.range_inputs.append(d)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        if any(t in SKIP_TAGS for t, _ in self.stack):
            return
        tag = self.stack[-1][0] if self.stack else ""
        active = self._active_classes()
        colored = bool(active & EPISTEMIC_CLASSES)
        self.text_nodes.append((text, tag, active, colored))


# ---------------------------------------------------------------- checks


def check_placeholders(html, findings):
    hits = PLACEHOLDER_RE.findall(html)
    # Deduplicate but keep order.
    seen, uniq = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h)
            uniq.append(h)
    if uniq:
        sample = ", ".join(uniq[:6])
        more = " (+{} more)".format(len(uniq) - 6) if len(uniq) > 6 else ""
        findings.append(Finding(
            "error", "PLACEHOLDER",
            "{} unfilled template placeholder(s) remain".format(len(uniq)),
            sample + more,
        ))


def check_color_coverage(parser, findings, strict):
    """Every figure in a display slot must declare where it came from."""
    untyped, total = [], 0
    prose_figures = 0

    for text, tag, classes, _ in parser.text_nodes:
        n = len(NUMERIC_RE.findall(text))
        if not n:
            continue
        in_slot = tag in DISPLAY_SLOT_TAGS or bool(classes & DISPLAY_SLOT_CLASSES)
        if not in_slot or classes & SKIP_CLASSES:
            prose_figures += n
            continue
        total += n
        if not (classes & ACCEPTED_TYPINGS):
            for match in NUMERIC_RE.findall(text):
                untyped.append((match, text[:60]))

    if total == 0 and prose_figures == 0:
        findings.append(Finding(
            "error", "NO-NUMBERS",
            "no significant figures found — this does not look like a research deliverable",
        ))
        return
    if total == 0:
        findings.append(Finding(
            "warn", "NO-SLOTS",
            "{} figures found but none in a KPI tile, table cell, or dial output — "
            "the analysis is all prose".format(prose_figures),
        ))
        return

    ratio = (total - len(untyped)) / total
    if untyped:
        sample = "; ".join('"{}" in "{}…"'.format(m, c) for m, c in untyped[:4])
        level = "error" if (ratio < 0.25 or strict) else "warn"
        findings.append(Finding(
            level, "UNTYPED",
            "{}/{} display-slot figures carry no provenance class ({:.0%} typed)".format(
                len(untyped), total, ratio),
            sample,
        ))


def check_legend(parser, findings):
    if not parser.has_legend:
        findings.append(Finding(
            "error", "NO-LEGEND",
            "no .legend or .flowlegend block — the color system must be explained "
            "before the first colored number",
        ))


def check_disclosure(html_lower, findings):
    if not any(m in html_lower for m in DISCLOSURE_MARKERS):
        findings.append(Finding(
            "error", "NO-DISCLOSURE",
            "no disclosure block found (expected 'not financial advice' / "
            "'do your own research' / adviser status)",
        ))


def check_sources(html_lower, findings):
    if not any(m in html_lower for m in SOURCE_MARKERS):
        findings.append(Finding(
            "error", "NO-SOURCES",
            "no source attribution found — every deliverable needs sources with as-of dates",
        ))
    # A four-digit year alone is not a date stamp; look for a month or explicit as-of.
    dated = re.search(
        r"\b(as of|dated)\b|"
        r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b|"
        r"\b\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b",
        html_lower,
    )
    if not dated:
        findings.append(Finding(
            "warn", "NO-ASOF",
            "no explicit as-of date found; figures go stale and readers cannot tell when",
        ))


def check_navigation(parser, html, findings, mode):
    if mode == "deck":
        if parser.slides < 5:
            findings.append(Finding(
                "error", "SLIDE-COUNT",
                "only {} slide(s) found; the deck arc needs at least 5".format(parser.slides),
            ))
        elif parser.slides > 14:
            findings.append(Finding(
                "warn", "SLIDE-COUNT",
                "{} slides exceeds the 14-slide ceiling — consider splitting".format(parser.slides),
            ))
        # Count only the attribute on real elements — the CSS selector
        # [data-on="1"] appears many times inside <style> and must not count.
        active = len(re.findall(r'<section[^>]*\bdata-on="1"', html))
        if active != 1:
            findings.append(Finding(
                "error", "NAV-STATE",
                'expected exactly one slide with data-on="1", found {}'.format(active),
            ))
        for needed in ("id=\"stage\"", "id=\"dots\"", "id=\"prev\"", "id=\"next\""):
            if needed not in html:
                findings.append(Finding(
                    "error", "NAV-BROKEN",
                    "navigation element missing: {}".format(needed),
                ))
    else:
        if parser.sections < 4:
            findings.append(Finding(
                "warn", "SECTION-COUNT",
                "only {} id'd sections; the dashboard arc expects ~7".format(parser.sections),
            ))
        anchors = set(re.findall(r'href="#([\w-]+)"', html))
        ids = set(re.findall(r'<section id="([\w-]+)"', html))
        dangling = anchors - ids
        if dangling:
            findings.append(Finding(
                "error", "DEAD-ANCHOR",
                "nav links point at missing sections: {}".format(", ".join(sorted(dangling))),
            ))


def check_accessibility(parser, html, findings):
    for d in parser.range_inputs:
        if not d.get("aria-label") and not d.get("aria-labelledby"):
            findings.append(Finding(
                "error", "A11Y-RANGE",
                "range input has no aria-label naming its units",
            ))
    unlabeled = [
        d for d in parser.buttons
        if not d.get("aria-label") and not d.get("id") == "cur"
    ]
    if len(unlabeled) > 2:
        findings.append(Finding(
            "warn", "A11Y-BUTTON",
            "{} button(s) without aria-label".format(len(unlabeled)),
        ))
    if "prefers-reduced-motion" not in html:
        findings.append(Finding(
            "error", "A11Y-MOTION",
            "no prefers-reduced-motion block; animated bars will sit at zero for "
            "users who disable motion",
        ))
    elif re.search(r"prefers-reduced-motion", html) and "--h" in html:
        block = html[html.find("prefers-reduced-motion"):]
        block = block[: block.find("}\n}") + 3] if "}\n}" in block else block[:600]
        if "var(--h)" not in block:
            findings.append(Finding(
                "warn", "A11Y-MOTION-BARS",
                "reduced-motion block does not restore bar heights (height:var(--h)); "
                "charts may render empty",
            ))
    if 'lang=' not in html[:400]:
        findings.append(Finding("warn", "A11Y-LANG", "<html> has no lang attribute"))


def check_tables(parser, findings):
    if parser.tables and parser.scroll_wrapped_tables < parser.tables:
        findings.append(Finding(
            "warn", "TABLE-SCROLL",
            "{}/{} tables lack an overflow-x container; the page body may scroll "
            "sideways on mobile".format(
                parser.tables - parser.scroll_wrapped_tables, parser.tables),
        ))


def check_fairness(html_lower, findings):
    cues = ("be fair", "in plain terms", "where this could be wrong",
            "what could go wrong", "kill criteria", "bear", "known gaps",
            "limitations")
    present = [c for c in cues if c in html_lower]
    if len(present) < 2:
        findings.append(Finding(
            "warn", "NO-COUNTERCASE",
            "found {} of the expected counter-argument cues ({}) — a deliverable "
            "without a bear case or fairness caveat reads as promotion".format(
                len(present), ", ".join(repr(c) for c in cues[:4])),
        ))


# ---------------------------------------------------------------- driver


def detect_mode(html):
    if 'class="slide"' in html or "class='slide'" in html:
        return "deck"
    return "dashboard"


def validate(path, strict=False):
    html = path.read_text(encoding="utf-8", errors="replace")
    lower = html.lower()
    mode = detect_mode(html)

    parser = DeckParser()
    parser.feed(html)
    parser.close()

    findings = []
    check_placeholders(html, findings)
    check_color_coverage(parser, findings, strict)
    check_legend(parser, findings)
    check_disclosure(lower, findings)
    check_sources(lower, findings)
    check_navigation(parser, html, findings, mode)
    check_accessibility(parser, html, findings)
    check_tables(parser, findings)
    check_fairness(lower, findings)

    return mode, parser, findings


def main():
    ap = argparse.ArgumentParser(
        description="Structural QA for equity-research-deck HTML output.")
    ap.add_argument("file", help="path to the generated .html deliverable")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as errors")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print("validate_deck: no such file: {}".format(path), file=sys.stderr)
        return 2

    mode, parser, findings = validate(path, args.strict)

    units = parser.slides if mode == "deck" else parser.sections
    label = "slides" if mode == "deck" else "sections"
    print("\nvalidate_deck — {}".format(path.name))
    print("  mode: {}  ·  {}: {}  ·  tables: {}".format(
        mode, label, units, parser.tables))
    print("")

    errors = [f for f in findings if f.level == "error"]
    warns = [f for f in findings if f.level == "warn"]

    if not findings:
        print("  PASS — no structural issues found.")
        print("\n  Structure is not substance. Read the deck.\n")
        return 0

    for f in errors + warns:
        print(f.render())

    print("\n  {} error(s), {} warning(s)".format(len(errors), len(warns)))
    if errors or (args.strict and warns):
        print("  FAIL\n")
        return 1
    print("  PASS with warnings\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
