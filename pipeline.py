#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRISMA 3-Phase Screening Pipeline
==================================
Phase 1: 重複削除
Phase 2: 学会ランク A/A* 絞り込み (CORE.csv 参照)
Phase 3: キーワードマッチングによる除外

各フェーズで詳細ログと結果CSVを個別出力。
"""

from __future__ import annotations
import argparse, csv, re, sys
from collections import defaultdict
from pathlib import Path
import difflib

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
DEFAULT_INPUT   = _HERE / "ResearchVR2.csv"
DEFAULT_CORE    = _HERE / "CORE.csv"
DEFAULT_SJR     = _HERE / "scimagojr 2025.csv"
DEFAULT_OUTDIR  = _HERE

# ---------------------------------------------------------------------------
# Column aliases
# ---------------------------------------------------------------------------
TITLE_ALIASES    = ["Title", "title", "TITLE"]
ABSTRACT_ALIASES = ["Abstract Note", "Abstract", "abstract", "ABSTRACT",
                     "abstract_note", "AbstractNote"]
VENUE_ALIASES    = ["Publication Title", "publication_title", "Venue",
                    "journal", "booktitle", "Conference Name", "Meeting Name"]
DOI_ALIASES      = ["DOI", "doi"]
KEY_ALIASES      = ["Key", "key"]
ISSN_ALIASES     = ["ISSN", "issn", "ISBN"]

# ---------------------------------------------------------------------------
# CORE rank priority  (高いほど上位)
# ---------------------------------------------------------------------------
RANK_ORDER = {"A*": 4, "A": 3, "B": 2, "C": 1}
HIGH_RANKS = {"A*", "A"}   # Phase 2 で採用するランク

# ---------------------------------------------------------------------------
# Keyword Exclusion Categories  (Phase 3)
# ---------------------------------------------------------------------------
EXCLUSION_CATEGORIES: list[tuple[str, list[str]]] = [
    (
        "Cat1 [Not VR / Out of Scope]",
        [
            r"\bdesktop display\b", r"\bdesktop monitor\b", r"\bcomputer monitor\b",
            r"\bflat[- ]screen\b", r"\bflat panel\b", r"\b2d display\b",
            r"\baugmented reality\b", r"\bmixed reality\b",
            r"\bar\b", r"\bmr\b",
            r"\b360[- ]?(?:degree[s]?\s+)?video\b", r"\bspherical video\b",
            r"\bpanoramic video\b", r"\bomnidirectional video\b",
            r"\bsmartphone\b", r"\bmobile phone\b", r"\btablet(?:\s+computer)?\b",
            r"\bprojection mapping\b", r"\bprojected display\b",
            r"\bcave automatic virtual\b", r"\bcave system\b", r"\bcave display\b",
        ],
    ),
    (
        "Cat2 [Tech / Non-Empirical]",
        [
            r"\brendering\s+(?:algorithm|engine|pipeline|technique|performance)\b",
            r"\breal[- ]?time\s+rendering\b", r"\bshader\b", r"\bgpu\b",
            r"\bpoint\s+cloud\b", r"\bdepth\s+camera\b", r"\bstereo\s+reconstruction\b",
            r"\bmotion[- ]to[- ]photon\b", r"\bframe\s+rate\b", r"\brefresh\s+rate\b",
            r"\btracking\s+algorithm\b", r"\bsegmentation\s+algorithm\b",
            r"\boptimiz(?:ation|ing)\s+algorithm\b",
            r"\btechnical\s+report\b", r"\bsystem\s+architecture\b",
            r"\bsoftware\s+(?:framework|architecture|library)\b",
        ],
    ),
    (
        "Cat3 [Clinical / Medical]",
        [
            r"\brehabilitation\b", r"\bphysical\s+therapy\b",
            r"\boccupational\s+therapy\b",
            r"\bcognitive\s+(?:behavioural|behavioral)\s+therapy\b",
            r"\bexposure\s+therapy\b", r"\btherapeutic\s+intervention\b",
            r"\bsurgical\s+(?:training|simulation|procedure|planning)\b",
            r"\bsurgery\b", r"\blaparoscop\w+\b", r"\bminimally\s+invasive\b",
            r"\bstroke\s+(?:patient|rehabilitation|survivor|recovery)\b",
            r"\bpatient[s]?\b",
            r"\bclinical\s+(?:trial|study|outcome|setting|population)\b",
            r"\bphobia\b", r"\bptsd\b", r"\bpost[- ]traumatic\s+stress\b",
            r"\bautism\s+spectrum\b", r"\bdementia\b", r"\balzheimer\b",
            r"\bchronic\s+pain\b", r"\bpain\s+management\b", r"\bpain\s+relief\b",
            r"\bneurological\s+(?:disorder|condition|rehabilitation|disease)\b",
            r"\bpsychiatric\s+(?:disorder|treatment|patient)\b",
            r"\bpsychosis\b", r"\bschizophrenia\b",
        ],
    ),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_col(fieldnames: list[str], aliases: list[str]) -> str | None:
    for a in aliases:
        if a in fieldnames:
            return a
    return None


def normalize_venue(name: str) -> str:
    if not name:
        return ""
    n = name.lower()
    # Remove 4-digit years (e.g. 2010, 2024)
    n = re.sub(r"\b\d{4}\b", " ", n)
    # Remove ordinals (e.g. 1st, 2nd, 3rd, 10th)
    n = re.sub(r"\b\d+(?:st|nd|rd|th)\b", " ", n)
    # Remove parenthesised content entirely (e.g. "(VR)", "(ISMAR)", "(CW)")
    n = re.sub(r"\([^)]*\)", " ", n)
    # Remove non-word characters
    n = re.sub(r"[^\w\s]", " ", n)
    stop = [
        r"proceedings\s+of", r"proc\s+of", r"proc",
        r"conference\s+on", r"journal\s+of", r"transactions\s+on",
        r"symposium\s+on", r"international", r"the", r"of", r"on",
        r"in", r"and",
        r"annual", r"workshop", r"adjunct", r"abstracts",
        r"workshops", r"poster", r"posters",
    ]
    for sw in stop:
        n = re.sub(r"\b" + sw + r"\b", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def extract_parenthesized_acronym(name: str) -> str:
    """Return text inside the last parentheses if it looks like an acronym,
    e.g. '2010 IEEE VR Conference (VR)' -> 'VR'"""
    m = re.search(r"\(([^)]+)\)\s*$", name.strip())
    if m:
        candidate = m.group(1).strip()
        # Accept if it looks like an acronym: short, mostly uppercase letters/digits
        if re.match(r"^[A-Za-z][A-Za-z0-9 \-]{0,20}$", candidate):
            return candidate
    return ""


def load_core(core_path: Path) -> dict:
    """
    Returns dict: normalized_key -> {original_title, acronym, rank}
    CORE.csv format (no header):
      col0=id, col1=Title, col2=Acronym, col3=Source, col4=Rank, ...
    """
    core: dict = {}
    with core_path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 5:
                continue
            title   = row[1].strip()
            acronym = row[2].strip()
            rank    = row[4].strip()
            if not title:
                continue
            norm = normalize_venue(title)
            entry = {"original_title": title, "acronym": acronym, "rank": rank}
            core[norm] = entry
            if acronym:
                core[acronym.lower()] = entry
    return core


def load_sjr(sjr_path: Path) -> dict:
    """
    Returns dict: normalized_key -> {original_title, quartile}
    Also indexes by ISSN (comma-separated) for fast matching.
    scimagojr CSV uses semicolons as separator.
    """
    sjr: dict = {}
    issn_index: dict = {}  # issn -> entry
    with sjr_path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader, [])
        try:
            title_idx = header.index("Title")
            q_idx     = header.index("SJR Best Quartile")
            issn_idx  = header.index("Issn") if "Issn" in header else -1
        except ValueError:
            print(f"[WARNING] SJR file header not as expected: {header[:6]}")
            return sjr
        for row in reader:
            if len(row) <= max(title_idx, q_idx):
                continue
            title    = row[title_idx].strip().strip('"')
            quartile = row[q_idx].strip().strip('"')
            if not title:
                continue
            norm  = normalize_venue(title)
            entry = {"original_title": title, "quartile": quartile}
            sjr[norm]          = entry
            sjr[title.lower()] = entry
            # ISSN index
            if issn_idx >= 0 and issn_idx < len(row):
                issns_raw = row[issn_idx].strip().strip('"')
                for issn in re.split(r"[,\s]+", issns_raw):
                    issn = issn.strip().replace("-", "")
                    if issn:
                        issn_index[issn] = entry
    # Store ISSN index inside sjr under special key
    sjr["__issn_index__"] = issn_index  # type: ignore
    return sjr


_venue_cache: dict[str, tuple] = {}

_sjr_cache: dict[str, tuple] = {}


def _fuzzy_best(norm: str, db: dict, threshold: float):
    """Return (matched_key, score) or (None, 0) via length-pruned fuzzy search."""
    best_score, best_key = 0.0, None
    for k in db:
        max_len = max(len(norm), len(k))
        if max_len == 0:
            continue
        if abs(len(norm) - len(k)) > max_len * (1 - threshold):
            continue
        s = difflib.SequenceMatcher(None, norm, k).ratio()
        if s > best_score:
            best_score, best_key = s, k
    return best_key, best_score


def best_core_match(venue: str, core: dict, threshold: float = 0.82):
    """Cached CORE venue lookup.
    Priority: (1) exact norm, (2) acronym in parentheses, (3) fuzzy.
    """
    if venue in _venue_cache:
        return _venue_cache[venue]
    norm = normalize_venue(venue)
    low  = venue.strip().lower()

    # 1. Exact on normalized name
    if norm and norm in core:
        r = (core[norm]["original_title"], core[norm]["rank"])
        _venue_cache[venue] = r
        return r

    # 2. Exact on lowercase original
    if low in core:
        r = (core[low]["original_title"], core[low]["rank"])
        _venue_cache[venue] = r
        return r

    # 3. Match acronym extracted from parentheses (e.g. "2010 IEEE VR Conference (VR)" -> "VR")
    acronym = extract_parenthesized_acronym(venue)
    if acronym:
        acr_low = acronym.lower()
        if acr_low in core:
            r = (core[acr_low]["original_title"], core[acr_low]["rank"])
            _venue_cache[venue] = r
            return r
        # Also try normalized acronym
        acr_norm = normalize_venue(acronym)
        if acr_norm and acr_norm in core:
            r = (core[acr_norm]["original_title"], core[acr_norm]["rank"])
            _venue_cache[venue] = r
            return r

    # 4. Fuzzy on normalized name (CORE only, ~800 entries, fast enough)
    if norm:
        bk, bs = _fuzzy_best(norm, core, threshold)
        r = (core[bk]["original_title"], core[bk]["rank"]) if bs >= threshold and bk else (None, None)
    else:
        r = (None, None)
    _venue_cache[venue] = r
    return r


def best_sjr_match(venue: str, sjr: dict, issn: str = "", threshold: float = 0.82):
    """Cached SJR lookup: exact title match only (no fuzzy - too slow at 32k entries).
    Falls back to ISSN lookup if provided."""
    cache_key = f"{venue}||{issn}"
    if cache_key in _sjr_cache:
        return _sjr_cache[cache_key]

    issn_index = sjr.get("__issn_index__", {})

    # 1. ISSN lookup (fastest)
    for raw_issn in re.split(r"[,\s]+", issn):
        raw_issn = raw_issn.strip().replace("-", "")
        if raw_issn and raw_issn in issn_index:
            entry = issn_index[raw_issn]
            r = (entry["original_title"], entry["quartile"])
            _sjr_cache[cache_key] = r
            return r

    # 2. Exact normalized title
    norm = normalize_venue(venue)
    low  = venue.strip().lower()
    if norm and norm in sjr and norm != "__issn_index__":
        entry = sjr[norm]
        r = (entry["original_title"], entry["quartile"])
        _sjr_cache[cache_key] = r
        return r
    if low in sjr and low != "__issn_index__":
        entry = sjr[low]
        r = (entry["original_title"], entry["quartile"])
        _sjr_cache[cache_key] = r
        return r

    _sjr_cache[cache_key] = (None, None)
    return None, None


def compile_exclusions(cats):
    return [(lbl, [(p, re.compile(p, re.IGNORECASE)) for p in pats])
            for lbl, pats in cats]


def screen_keywords(text: str, compiled_cats):
    matched_cats, matched_kws = [], []
    for lbl, cpats in compiled_cats:
        for raw, rx in cpats:
            if rx.search(text):
                if lbl not in matched_cats:
                    matched_cats.append(lbl)
                matched_kws.append(f"{lbl}::{raw}")
    return matched_cats, matched_kws


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

# ---------------------------------------------------------------------------
# Phase 1: Deduplication
# ---------------------------------------------------------------------------

def phase1_dedup(rows: list[dict], fieldnames: list[str],
                 outdir: Path, log_lines: list[str]) -> list[dict]:
    SEP = "=" * 72
    log_lines += [SEP, "  PHASE 1: DEDUPLICATION", SEP, ""]

    title_col = resolve_col(fieldnames, TITLE_ALIASES)
    doi_col   = resolve_col(fieldnames, DOI_ALIASES)
    key_col   = resolve_col(fieldnames, KEY_ALIASES)

    log_lines.append(f"  Input records          : {len(rows):>8,}")
    log_lines.append(f"  Title column           : {title_col!r}")
    log_lines.append(f"  DOI column             : {doi_col!r}")
    log_lines.append(f"  Key column             : {key_col!r}")
    log_lines.append("")

    seen_doi: dict[str, int]   = {}
    seen_title: dict[str, int] = {}
    seen_key: dict[str, int]   = {}

    dedup: list[dict] = []
    dup_doi_count   = 0
    dup_title_count = 0
    dup_key_count   = 0

    for i, row in enumerate(rows):
        doi   = (row.get(doi_col,   "") or "").strip().lower() if doi_col   else ""
        title = (row.get(title_col, "") or "").strip().lower() if title_col else ""
        key   = (row.get(key_col,   "") or "").strip()         if key_col   else ""

        dup_reason = ""
        if doi and doi in seen_doi:
            dup_doi_count += 1
            dup_reason = f"Duplicate DOI (first seen at row {seen_doi[doi]})"
        elif key and key in seen_key:
            dup_key_count += 1
            dup_reason = f"Duplicate Key (first seen at row {seen_key[key]})"
        elif title and title in seen_title:
            dup_title_count += 1
            dup_reason = f"Duplicate Title (first seen at row {seen_title[title]})"

        if dup_reason:
            continue

        if doi:   seen_doi[doi]     = i
        if key:   seen_key[key]     = i
        if title: seen_title[title] = i
        dedup.append(row)

    removed = len(rows) - len(dedup)
    log_lines.append(f"  Removed by DOI match   : {dup_doi_count:>8,}")
    log_lines.append(f"  Removed by Key match   : {dup_key_count:>8,}")
    log_lines.append(f"  Removed by Title match : {dup_title_count:>8,}")
    log_lines.append(f"  Total removed          : {removed:>8,}")
    log_lines.append(f"  Records after dedup    : {len(dedup):>8,}")
    log_lines.append("")

    # Write output
    out_path = outdir / "step1_dedup.csv"
    write_csv(out_path, dedup, fieldnames)
    log_lines.append(f"  Output -> {out_path.name}")
    log_lines.append("")

    # Console
    print(f"\n{'='*60}")
    print(f"  PHASE 1: Deduplication")
    print(f"{'='*60}")
    print(f"  Input     : {len(rows):,}")
    print(f"  Removed   : {removed:,}  (DOI:{dup_doi_count} Key:{dup_key_count} Title:{dup_title_count})")
    print(f"  Remaining : {len(dedup):,}")
    print(f"  Output    : {out_path.name}")

    return dedup

# ---------------------------------------------------------------------------
# Phase 2: CORE Rank Filtering (A / A* only)
# ---------------------------------------------------------------------------

def phase2_core(rows: list[dict], fieldnames: list[str],
                core: dict, sjr: dict, outdir: Path, log_lines: list[str]) -> list[dict]:
    SEP = "=" * 72
    log_lines += [SEP, "  PHASE 2: CORE A/A* + SJR Q1 SCREENING", SEP, ""]

    venue_col = resolve_col(fieldnames, VENUE_ALIASES)
    issn_col  = resolve_col(fieldnames, ISSN_ALIASES)
    log_lines.append(f"  Input records   : {len(rows):>8,}")
    log_lines.append(f"  Venue column    : {venue_col!r}")
    log_lines.append(f"  CORE entries    : {len(core):>8,}")
    log_lines.append(f"  SJR entries     : {len(sjr):>8,}")
    log_lines.append("")

    included: list[dict] = []
    excluded: list[dict] = []

    stats: dict[str, int] = defaultdict(int)
    rank_dist: dict[str, int] = defaultdict(int)   # CORE ranks
    sjr_q_dist: dict[str, int] = defaultdict(int)  # SJR quartiles
    unmatched_venues: list[str] = []

    out_fields_incl = fieldnames + ["Matched_Venue", "Ranking_Source", "CORE_Rank", "SJR_Quartile"]
    out_fields_excl = fieldnames + ["Matched_Venue", "Ranking_Source", "CORE_Rank", "SJR_Quartile", "Excl_Reason_Phase2"]

    for row in rows:
        raw_venue = (row.get(venue_col, "") or "") if venue_col else ""

        # --- Step A: CORE lookup ---
        matched_title, rank = best_core_match(raw_venue, core)

        if matched_title is not None:
            row["Matched_Venue"]   = matched_title
            row["Ranking_Source"]  = "CORE"
            row["CORE_Rank"]       = rank
            row["SJR_Quartile"]    = ""
            rank_dist[rank]       += 1
            if rank in HIGH_RANKS:
                stats["core_included"] += 1
                row["Excl_Reason_Phase2"] = ""
                included.append(row)
            else:
                stats["core_low_rank"] += 1
                row["Excl_Reason_Phase2"] = f"CORE Rank '{rank}' < A"
                excluded.append(row)
            continue

        # --- Step B: SJR lookup (for journals not in CORE) ---
        raw_issn  = (row.get(issn_col, "") or "") if issn_col else ""
        sjr_title, quartile = best_sjr_match(raw_venue, sjr, issn=raw_issn)

        if sjr_title is not None:
            row["Matched_Venue"]   = sjr_title
            row["Ranking_Source"]  = "SJR"
            row["CORE_Rank"]       = ""
            row["SJR_Quartile"]    = quartile
            sjr_q_dist[quartile]  += 1
            if quartile == "Q1":
                stats["sjr_included"] += 1
                row["Excl_Reason_Phase2"] = ""
                included.append(row)
            else:
                stats["sjr_low_rank"] += 1
                row["Excl_Reason_Phase2"] = f"SJR Quartile '{quartile}' is not Q1"
                excluded.append(row)
            continue

        # --- Not found in either DB ---
        stats["unmatched"] += 1
        unmatched_venues.append(raw_venue or "(empty)")
        row["Matched_Venue"]      = ""
        row["Ranking_Source"]     = ""
        row["CORE_Rank"]          = ""
        row["SJR_Quartile"]       = ""
        row["Excl_Reason_Phase2"] = "Venue not found in CORE or SJR"
        excluded.append(row)

    total_included = stats.get("core_included", 0) + stats.get("sjr_included", 0)

    log_lines.append("  --- CORE Rank Distribution ---")
    for r, cnt in sorted(rank_dist.items(), key=lambda x: -RANK_ORDER.get(x[0], 0)):
        log_lines.append(f"    CORE {r:<16}: {cnt:>6,}")
    log_lines.append("")
    log_lines.append("  --- SJR Quartile Distribution ---")
    for q in ["Q1", "Q2", "Q3", "Q4", "-"]:
        cnt = sjr_q_dist.get(q, 0)
        if cnt:
            log_lines.append(f"    SJR  {q:<16}: {cnt:>6,}")
    log_lines.append("")
    log_lines.append(f"  INCLUDED total         : {total_included:>8,}")
    log_lines.append(f"    CORE A/A*            : {stats.get('core_included',0):>8,}")
    log_lines.append(f"    SJR Q1               : {stats.get('sjr_included',0):>8,}")
    log_lines.append(f"  EXCLUDED total         : {len(excluded):>8,}")
    log_lines.append(f"    CORE low rank (B/C)  : {stats.get('core_low_rank',0):>8,}")
    log_lines.append(f"    SJR Q2/Q3/Q4         : {stats.get('sjr_low_rank',0):>8,}")
    log_lines.append(f"    Unmatched            : {stats.get('unmatched',0):>8,}")
    log_lines.append("")

    if unmatched_venues:
        log_lines.append("  --- Sample Unmatched Venues (first 30) ---")
        for v in unmatched_venues[:30]:
            log_lines.append(f"    {v}")
        if len(unmatched_venues) > 30:
            log_lines.append(f"    ... and {len(unmatched_venues)-30} more")
        log_lines.append("")

    # Write outputs
    incl_path = outdir / "step2_rank_included.csv"
    excl_path = outdir / "step2_rank_excluded.csv"
    write_csv(incl_path, included, out_fields_incl)
    write_csv(excl_path, excluded, out_fields_excl)

    log_lines.append(f"  Included output -> {incl_path.name}")
    log_lines.append(f"  Excluded output -> {excl_path.name}")
    log_lines.append("")

    # Console
    print(f"\n{'='*60}")
    print(f"  PHASE 2: CORE A/A* + SJR Q1 Screening")
    print(f"{'='*60}")
    print(f"  Input          : {len(rows):,}")
    print(f"  Included total : {total_included:,}")
    print(f"    CORE A/A*    : {stats.get('core_included',0):,}")
    print(f"    SJR Q1       : {stats.get('sjr_included',0):,}")
    print(f"  Excluded       : {len(excluded):,}")
    print(f"    CORE low     : {stats.get('core_low_rank',0):,}")
    print(f"    SJR Q2+      : {stats.get('sjr_low_rank',0):,}")
    print(f"    Unmatched    : {stats.get('unmatched',0):,}")
    print(f"  Incl CSV  : {incl_path.name}")
    print(f"  Excl CSV  : {excl_path.name}")

    return included

# ---------------------------------------------------------------------------
# Phase 3: Keyword Exclusion
# ---------------------------------------------------------------------------

def phase3_keywords(rows: list[dict], fieldnames: list[str],
                    outdir: Path, log_lines: list[str]) -> list[dict]:
    SEP = "=" * 72
    log_lines += [SEP, "  PHASE 3: KEYWORD EXCLUSION", SEP, ""]

    title_col    = resolve_col(fieldnames, TITLE_ALIASES)
    abstract_col = resolve_col(fieldnames, ABSTRACT_ALIASES)
    compiled     = compile_exclusions(EXCLUSION_CATEGORIES)

    log_lines.append(f"  Input records   : {len(rows):>8,}")
    log_lines.append(f"  Title column    : {title_col!r}")
    log_lines.append(f"  Abstract column : {abstract_col!r}")
    log_lines.append("")

    included: list[dict] = []
    excluded: list[dict] = []
    cat_counts: dict[str, int] = defaultdict(int)
    kw_counts:  dict[str, int] = defaultdict(int)

    out_fields_incl = list(fieldnames)
    for f in ["Matched_Venue", "Ranking_Source", "CORE_Rank", "SJR_Quartile"]:
        if f not in out_fields_incl:
            out_fields_incl.append(f)

    out_fields_excl = out_fields_incl + ["KW_Excl_Category", "KW_Excl_Keywords"]

    for row in rows:
        title    = (row.get(title_col,    "") or "") if title_col    else ""
        abstract = (row.get(abstract_col, "") or "") if abstract_col else ""
        haystack = f"{title} {abstract}".lower()

        matched_cats, matched_kws = screen_keywords(haystack, compiled)

        if matched_cats:
            row["KW_Excl_Category"] = " | ".join(matched_cats)
            row["KW_Excl_Keywords"]  = " | ".join(matched_kws)
            excluded.append(row)
            for c in matched_cats:
                cat_counts[c] += 1
            for k in matched_kws:
                kw_counts[k]  += 1
        else:
            included.append(row)

    total = len(rows)
    log_lines.append(f"  Included        : {len(included):>8,}  ({len(included)/total*100:.1f} %)")
    log_lines.append(f"  Excluded        : {len(excluded):>8,}  ({len(excluded)/total*100:.1f} %)")
    log_lines.append("")
    log_lines.append("  --- By Category ---")
    for lbl, _ in EXCLUSION_CATEGORIES:
        n = cat_counts.get(lbl, 0)
        log_lines.append(f"    {n:>6,}  {lbl}")
    log_lines.append("")
    log_lines.append("  --- By Keyword (top hits) ---")
    for lbl, pats in EXCLUSION_CATEGORIES:
        log_lines.append(f"  +-- {lbl}")
        kw_rows = [(p, kw_counts.get(f"{lbl}::{p}", 0)) for p in pats]
        for p, cnt in sorted(kw_rows, key=lambda x: -x[1]):
            if cnt > 0:
                log_lines.append(f"  |  {cnt:>6,}  {p}")
        log_lines.append("  |")
    log_lines.append("")
    log_lines.append("  --- Silent Patterns (zero hits) ---")
    for lbl, pats in EXCLUSION_CATEGORIES:
        silent = [p for p in pats if kw_counts.get(f"{lbl}::{p}", 0) == 0]
        if silent:
            log_lines.append(f"  {lbl}")
            for p in silent:
                log_lines.append(f"    {p}")

    # Write outputs
    incl_path = outdir / "step3_kw_included.csv"
    excl_path = outdir / "step3_kw_excluded.csv"
    write_csv(incl_path, included, out_fields_incl)
    write_csv(excl_path, excluded, out_fields_excl)

    log_lines.append("")
    log_lines.append(f"  Included output -> {incl_path.name}")
    log_lines.append(f"  Excluded output -> {excl_path.name}")
    log_lines.append("")

    # Console
    print(f"\n{'='*60}")
    print(f"  PHASE 3: Keyword Exclusion")
    print(f"{'='*60}")
    print(f"  Input     : {total:,}")
    print(f"  Included  : {len(included):,}  ({len(included)/total*100:.1f} %)")
    print(f"  Excluded  : {len(excluded):,}  ({len(excluded)/total*100:.1f} %)")
    for lbl, _ in EXCLUSION_CATEGORIES:
        n = cat_counts.get(lbl, 0)
        print(f"    {n:>6,}  {lbl}")
    print(f"  Incl CSV  : {incl_path.name}")
    print(f"  Excl CSV  : {excl_path.name}")

    return included

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description="3-Phase PRISMA Screening Pipeline")
    parser.add_argument("--input",  "-i", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--core",   "-c", type=Path, default=DEFAULT_CORE)
    parser.add_argument("--sjr",    "-s", type=Path, default=DEFAULT_SJR)
    parser.add_argument("--outdir", "-o", type=Path, default=DEFAULT_OUTDIR)
    args = parser.parse_args(argv)

    if not args.input.exists():
        sys.exit(f"[ERROR] Input not found: {args.input}")
    if not args.core.exists():
        sys.exit(f"[ERROR] CORE file not found: {args.core}")
    if not args.sjr.exists():
        sys.exit(f"[ERROR] SJR file not found: {args.sjr}")

    args.outdir.mkdir(parents=True, exist_ok=True)
    log_path = args.outdir / "pipeline_log.txt"
    log_lines: list[str] = [
        "=" * 72,
        "  PRISMA 3-Phase Screening Pipeline",
        f"  Input : {args.input}",
        f"  CORE  : {args.core}",
        "=" * 72,
        "",
    ]

    print(f"\n{'='*60}")
    print(f"  PRISMA Pipeline  |  {args.input.name}")
    print(f"{'='*60}")

    # Load input
    print(f"  Reading {args.input.name} ...")
    rows: list[dict] = []
    fieldnames: list[str] = []
    with args.input.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    print(f"  Loaded {len(rows):,} records, {len(fieldnames)} columns.")

    # Load CORE
    print(f"  Loading CORE rankings from {args.core.name} ...")
    core = load_core(args.core)
    print(f"  CORE entries loaded: {len(core):,}")

    # Load SJR
    print(f"  Loading SJR rankings from {args.sjr.name} ...")
    sjr = load_sjr(args.sjr)
    print(f"  SJR  entries loaded: {len(sjr):,}")

    # ── Phase 1 ──────────────────────────────────────────────
    after_p1 = phase1_dedup(rows, fieldnames, args.outdir, log_lines)

    # ── Phase 2 ──────────────────────────────────────────────
    after_p2 = phase2_core(after_p1, fieldnames, core, sjr, args.outdir, log_lines)

    # ── Phase 3 ──────────────────────────────────────────────
    after_p3 = phase3_keywords(after_p2, fieldnames, args.outdir, log_lines)

    # Summary
    SEP = "=" * 72
    log_lines += [
        SEP, "  PIPELINE SUMMARY", SEP, "",
        f"  Original records   : {len(rows):>8,}",
        f"  After dedup (P1)   : {len(after_p1):>8,}  (-{len(rows)-len(after_p1):,})",
        f"  After CORE  (P2)   : {len(after_p2):>8,}  (-{len(after_p1)-len(after_p2):,})",
        f"  After keywords (P3): {len(after_p3):>8,}  (-{len(after_p2)-len(after_p3):,})",
        "",
        "  Output files:",
        f"    step1_dedup.csv",
        f"    step2_rank_included.csv  (CORE A/A* + SJR Q1)",
        f"    step2_rank_excluded.csv",
        f"    step3_kw_included.csv   <- 最終候補",
        f"    step3_kw_excluded.csv",
        f"    pipeline_log.txt",
        "",
    ]

    with log_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print(f"\n{'='*60}")
    print(f"  PIPELINE SUMMARY")
    print(f"{'='*60}")
    print(f"  Original   : {len(rows):,}")
    print(f"  → Dedup    : {len(after_p1):,}")
    print(f"  → CORE A/A*: {len(after_p2):,}")
    print(f"  → Keywords : {len(after_p3):,}  ← 最終候補")
    print(f"\n  Log: {log_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
