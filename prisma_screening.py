#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
PRISMA Title / Abstract Screening  -  Automatic Keyword-Based Exclusion
=============================================================================

Phase  : Title/Abstract Screening (PRISMA Step 3)
Strategy: Conservative (recall > precision)
          - A paper is EXCLUDED only if it matches an exclusion keyword.
          - Papers with empty/missing abstracts are INCLUDED (handled later).

Input  : unique_papers.csv   (duplicate-removed Zotero CSV export)
Outputs:
  screened_included.csv   - papers advancing to full-text / abstract review
  screened_excluded.csv   - excluded papers with reason columns appended
  exclusion_summary.txt   - per-category and per-keyword exclusion counts

Column mapping (Zotero RIS/CSV export format):
  Title column   : "Title"
  Abstract column: "Abstract Note"

HOW TO USE
----------
1. Place this script and unique_papers.csv in the same directory.
2. Run:  python prisma_screening.py
3. Optional flags:
     --input  PATH   override input file path
     --outdir PATH   override output directory
     --dry-run       print summary without writing files

KEYWORD CONFIGURATION
---------------------
Edit EXCLUSION_CATEGORIES below to add / remove exclusion criteria.

Each entry is a tuple:
  ( "Category Label",  [list of regex patterns] )

All patterns are matched CASE-INSENSITIVELY with word-boundary guards (\\b)
so that abbreviations like "ar" / "mr" do NOT match sub-strings of other
words (e.g. "ar" will not match "virtual" or "library").

A paper is excluded if ANY pattern in ANY category matches.
All matching categories and keywords are recorded in the output.
=============================================================================
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Default I/O paths  (relative to this script's location)
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent
DEFAULT_INPUT  = _HERE / "unique_papers.csv"
DEFAULT_OUTDIR = _HERE

# ---------------------------------------------------------------------------
# Column name aliases
# Extend this list if your CSV uses different header names.
# ---------------------------------------------------------------------------

TITLE_ALIASES    = ["Title", "title", "TITLE"]
ABSTRACT_ALIASES = ["Abstract Note", "Abstract", "abstract", "ABSTRACT",
                    "abstract_note", "AbstractNote"]

# ---------------------------------------------------------------------------
# EXCLUSION KEYWORD CATEGORIES  <- Edit here to customise screening
# ---------------------------------------------------------------------------
#
# Screening rationale (conservative / high-recall):
#   Include everything that MIGHT be relevant; only exclude clear mismatches.
#
# Pattern notes:
#   - \b  = word boundary (prevents "ar" matching "virtual", "library", etc.)
#   - Use (?:...) for non-capturing groups if needed
#   - Patterns use Python `re` regex (IGNORECASE applied automatically)
# ---------------------------------------------------------------------------

EXCLUSION_CATEGORIES: list[tuple[str, list[str]]] = [

    # =========================================================================
    # Category 1 - Not VR / Out of Scope
    # Papers studying non-immersive displays or non-VR XR technologies.
    # =========================================================================
    (
        "Category 1 [Not VR / Out of Scope]",
        [
            # -- Non-immersive display hardware --------------------------------
            r"\bdesktop display\b",
            r"\bdesktop monitor\b",
            r"\bcomputer monitor\b",
            r"\bflat[- ]screen\b",
            r"\bflat panel\b",
            r"\b2d display\b",
            r"\bmonitor display\b",
            # NOTE: bare "monitor" is intentionally omitted - too polysemous
            #       (e.g. "to monitor performance", "heart rate monitor")

            # -- Augmented / Mixed Reality (not VR) ----------------------------
            r"\baugmented reality\b",
            r"\bmixed reality\b",
            # Short abbreviations - strictly word-boundary guarded
            r"\bar\b",          # AR  (e.g. "AR glasses", "AR overlay")
            r"\bmr\b",          # MR  (e.g. "MR headset", "MR system")

            # -- 360-degree / Omnidirectional video (passive, non-interactive) --
            r"\b360[- ]?(?:degree[s]?\s+)?video\b",
            r"\bspherical video\b",
            r"\bpanoramic video\b",
            r"\bomnidirectional video\b",

            # -- Mobile / handheld / projected displays ------------------------
            r"\bsmartphone\b",
            r"\bmobile phone\b",
            r"\btablet(?:\s+computer)?\b",
            r"\bprojection mapping\b",
            r"\bprojected display\b",

            # -- CAVE-type (room-scale projection, not HMD-VR) -----------------
            r"\bcave automatic virtual\b",
            r"\bcave system\b",
            r"\bcave display\b",
        ],
    ),

    # =========================================================================
    # Category 2 - Tech / Hardware / Non-Empirical
    # Papers that propose or evaluate systems/algorithms without a human
    # empirical study component.
    # =========================================================================
    (
        "Category 2 [Tech / Hardware / Non-Empirical]",
        [
            # -- Rendering / graphics engineering ------------------------------
            r"\brendering\s+(?:algorithm|engine|pipeline|technique|performance)\b",
            r"\breal[- ]?time\s+rendering\b",
            r"\bshader\b",
            r"\bgpu\b",
            r"\bpoint\s+cloud\b",
            r"\bdepth\s+camera\b",
            r"\bstereo\s+reconstruction\b",

            # -- Low-level performance / hardware parameters -------------------
            r"\b(?:end[- ]to[- ]end\s+)?latency\b",
            r"\bmotion[- ]to[- ]photon\b",
            r"\bframe\s+rate\b",
            r"\brefresh\s+rate\b",

            # -- Algorithms & optimisation without user study ------------------
            r"\btracking\s+algorithm\b",
            r"\bsegmentation\s+algorithm\b",
            r"\boptimiz(?:ation|ing)\s+algorithm\b",
            r"\boptimis(?:ation|ing)\s+algorithm\b",

            # -- Non-empirical publication types -------------------------------
            r"\bproceedings\s+of\b",
            r"\btechnical\s+report\b",
            r"\bsystem\s+architecture\b",
            r"\bsoftware\s+(?:framework|architecture|library)\b",
        ],
    ),

    # =========================================================================
    # Category 3 - Clinical / Medical
    # Papers whose primary context is clinical treatment, medical training,
    # or therapeutic intervention rather than HCI / behavioural research.
    # =========================================================================
    (
        "Category 3 [Clinical / Medical]",
        [
            # -- Rehabilitation & therapy --------------------------------------
            r"\brehabilitation\b",
            r"\bphysical\s+therapy\b",
            r"\boccupational\s+therapy\b",
            r"\bcognitive\s+(?:behavioural|behavioral)\s+therapy\b",
            r"\bexposure\s+therapy\b",
            r"\btherapeutic\s+intervention\b",
            # NOTE: bare "therapy" intentionally narrowed to avoid false positives

            # -- Surgery & clinical procedures ---------------------------------
            r"\bsurgical\s+(?:training|simulation|procedure|planning)\b",
            r"\bsurgery\b",
            r"\blaparoscop\w+\b",
            r"\bminimally\s+invasive\b",

            # -- Patient populations & medical conditions ----------------------
            r"\bstroke\s+(?:patient|rehabilitation|survivor|recovery)\b",
            r"\bpatient[s]?\b",
            r"\bclinical\s+(?:trial|study|outcome|setting|population)\b",
            r"\bphobia\b",
            r"\bptsd\b",
            r"\bpost[- ]traumatic\s+stress\b",
            r"\bautism\s+spectrum\b",
            r"\bdementia\b",
            r"\balzheimer\b",
            r"\bchronic\s+pain\b",
            r"\bpain\s+management\b",
            r"\bpain\s+relief\b",
            r"\bneurological\s+(?:disorder|condition|rehabilitation|disease)\b",
            r"\bpsychiatric\s+(?:disorder|treatment|patient)\b",
            r"\bpsychosis\b",
            r"\bschizophrenia\b",
        ],
    ),
]

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _compile(categories: list[tuple[str, list[str]]]):
    """Return categories with each pattern string replaced by a compiled re."""
    compiled = []
    for label, patterns in categories:
        compiled.append(
            (label, [(p, re.compile(p, re.IGNORECASE)) for p in patterns])
        )
    return compiled


def _resolve_col(fieldnames: list[str], aliases: list[str]) -> str | None:
    """Return the first alias that exists in fieldnames, else None."""
    for alias in aliases:
        if alias in fieldnames:
            return alias
    return None


def _screen(text: str, compiled_cats) -> tuple[list[str], list[str]]:
    """
    Check *text* against all compiled exclusion categories.

    Returns
    -------
    matched_cats : list[str]  - category labels that fired (may be empty)
    matched_kws  : list[str]  - "CategoryLabel::pattern" strings
    """
    matched_cats: list[str] = []
    matched_kws:  list[str] = []
    for cat_label, cpats in compiled_cats:
        for raw_pat, compiled_re in cpats:
            if compiled_re.search(text):
                if cat_label not in matched_cats:
                    matched_cats.append(cat_label)
                matched_kws.append(f"{cat_label}::{raw_pat}")
    return matched_cats, matched_kws


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _write_summary(
    path: Path,
    total: int,
    n_included: int,
    n_excluded: int,
    cat_counts: dict[str, int],
    kw_counts:  dict[str, int],
) -> None:
    W = 72
    lines: list[str] = []

    def h1(s=""):  lines.append("=" * W if not s else ("  " + s + "  ").center(W, "="))
    def h2(s=""):  lines.append("-" * W if not s else f"  {s}")
    def ln(s=""):  lines.append(s)

    h1()
    h1("PRISMA Title/Abstract Screening  -  Exclusion Summary")
    h1()
    ln()
    ln(f"  Total records processed  : {total:>8,}")
    ln(f"  Included (-> next phase) : {n_included:>8,}  ({n_included/total*100:5.1f} %)")
    ln(f"  Excluded (keyword match) : {n_excluded:>8,}  ({n_excluded/total*100:5.1f} %)")
    ln()
    h1()
    h2("BY CATEGORY  (papers matching >=1 keyword in that category)")
    h1()
    ln()
    for cat_label, _ in EXCLUSION_CATEGORIES:
        n = cat_counts.get(cat_label, 0)
        ln(f"  {cat_label}")
        ln(f"      {n:,} papers excluded")
        ln()

    h1()
    h2("BY KEYWORD  (sorted by hit count within each category)")
    h1()
    ln("  NOTE: one paper may be counted in multiple categories / keywords.")
    ln()
    for cat_label, cat_pats in EXCLUSION_CATEGORIES:
        ln(f"\n  +-- {cat_label}")
        kw_rows = []
        for raw_pat in cat_pats:        # cat_pats is a list of str patterns
            key = f"{cat_label}::{raw_pat}"
            kw_rows.append((raw_pat, kw_counts.get(key, 0)))
        for raw_pat, count in sorted(kw_rows, key=lambda x: -x[1]):
            if count > 0:
                ln(f"  |  {count:>6,}   {raw_pat}")
        if not any(c > 0 for _, c in kw_rows):
            ln("  |  (no matches)")
        ln("  +" + "-" * (W - 3))

    ln()
    h1()
    h2("PATTERNS THAT DID NOT FIRE (potential gaps / over-engineered filters)")
    h1()
    ln()
    for cat_label, cat_pats in EXCLUSION_CATEGORIES:
        silent = [p for p in cat_pats if kw_counts.get(f"{cat_label}::{p}", 0) == 0]
        if silent:
            ln(f"  {cat_label}")
            for p in silent:
                ln(f"      {p}")
            ln()

    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="PRISMA Title/Abstract screening with keyword exclusion."
    )
    parser.add_argument(
        "--input", "-i",
        type=Path, default=DEFAULT_INPUT,
        help=f"Input CSV (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--outdir", "-o",
        type=Path, default=DEFAULT_OUTDIR,
        help=f"Output directory (default: {DEFAULT_OUTDIR})",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Run screening but do NOT write output files; print summary only.",
    )
    args = parser.parse_args(argv)

    input_path: Path = args.input
    outdir: Path     = args.outdir

    # Validate input
    if not input_path.exists():
        sys.exit(
            f"\n[ERROR] Input file not found: {input_path}\n"
            f"  Please place unique_papers.csv in:\n  {_HERE}\n"
        )

    outdir.mkdir(parents=True, exist_ok=True)
    out_included = outdir / "screened_included.csv"
    out_excluded = outdir / "screened_excluded.csv"
    out_summary  = outdir / "exclusion_summary.txt"

    # Pre-compile patterns
    compiled = _compile(EXCLUSION_CATEGORIES)

    # Read & screen
    included:   list[dict] = []
    excluded:   list[dict] = []
    fieldnames: list[str]  = []

    cat_counts: dict[str, int] = defaultdict(int)
    kw_counts:  dict[str, int] = defaultdict(int)

    title_col: str | None    = None
    abstract_col: str | None = None

    sep = "=" * 60
    print(f"\n{sep}")
    print(f"  PRISMA Screening  -  reading {input_path.name}")
    print(f"{sep}")

    with input_path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])

        # Resolve column names
        title_col    = _resolve_col(fieldnames, TITLE_ALIASES)
        abstract_col = _resolve_col(fieldnames, ABSTRACT_ALIASES)

        if title_col is None:
            print(f"[WARNING] No title column found. Tried: {TITLE_ALIASES}")
        if abstract_col is None:
            print(f"[WARNING] No abstract column found. Tried: {ABSTRACT_ALIASES}")

        print(f"  Title column    : {title_col!r}")
        print(f"  Abstract column : {abstract_col!r}")
        print()

        for row in reader:
            title    = (row.get(title_col,    "") or "") if title_col    else ""
            abstract = (row.get(abstract_col, "") or "") if abstract_col else ""
            haystack = f"{title} {abstract}".lower()

            matched_cats, matched_kws = _screen(haystack, compiled)

            if matched_cats:
                row["exclusion_category"] = " | ".join(matched_cats)
                row["exclusion_keywords"]  = " | ".join(matched_kws)
                excluded.append(row)
                for cat in matched_cats:
                    cat_counts[cat] += 1
                for kw_label in matched_kws:
                    kw_counts[kw_label] += 1
            else:
                included.append(row)

    total = len(included) + len(excluded)
    if total == 0:
        sys.exit("[ERROR] No records found in the input CSV.")

    # Write outputs
    if not args.dry_run:
        excl_fields = fieldnames + ["exclusion_category", "exclusion_keywords"]
        _write_csv(out_included, included, fieldnames)
        _write_csv(out_excluded, excluded, excl_fields)
        _write_summary(out_summary, total, len(included), len(excluded),
                       cat_counts, kw_counts)

    # Console summary
    print(f"  {'Records processed':<30}: {total:>8,}")
    print(f"  {'Included (-> next phase)':<30}: {len(included):>8,}  ({len(included)/total*100:.1f} %)")
    print(f"  {'Excluded (keyword match)':<30}: {len(excluded):>8,}  ({len(excluded)/total*100:.1f} %)")
    print()
    print("  Breakdown by category:")
    for cat_label, _ in EXCLUSION_CATEGORIES:
        n = cat_counts.get(cat_label, 0)
        bar = "#" * min(40, int(n / max(total, 1) * 400))
        print(f"    {n:>6,}  {bar}  {cat_label}")
    print()

    if not args.dry_run:
        print("  Output files:")
        print(f"    {out_included}")
        print(f"    {out_excluded}")
        print(f"    {out_summary}")
    else:
        print("  [DRY RUN] No files written.")

    print(f"\n{sep}\n")


if __name__ == "__main__":
    main()
