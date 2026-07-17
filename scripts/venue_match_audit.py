#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
venue_match_audit.py — Phase 2 Venue「照合成功」側の誤り監査
================================================================================

【何を】
Phase 2 で CORE/SJR に「照合成功」とされた全 Venue について、
元Venue名 → マッチ先エントリ → 照合段階(正規化完全一致/小文字一致/括弧内頭字語/
ファジー)→ 類似度 を再導出して一覧化し、誤照合の疑いがあるものを抽出する。

【なぜ】
従来の監査(unmatched_venue_audit.py)は「未照合5,126件」のみを対象としており、
**誤照合(例: 'Presence'誌 → CORE 'Annual International Workshop on Presence')を
検出できない設計の穴があった**(Known-Item Test で Kilteni 2012 の誤除外として顕在化。
protocol_changelog.md Rev.6 に自己申告として記録)。本スクリプトは照合成功側を
全数監査し、Venue フィルタ全体の妥当性評価を完成させる。

【入力】
  - step2_rank_included.csv / step2_rank_excluded.csv(Matched_Venue 列を持つ)
  - CORE.csv / scimagojr 2025.csv

【出力】
  - outputs/venue_match_audit.csv     照合成功した全ユニークVenueの一覧
      (raw venue, matched entry, source, rank, match_stage, similarity, 件数, 採否)
  - outputs/venue_suspect_matches.csv 誤照合疑い(ファジー段階で類似度≤0.92、
      頭字語段階の全件、および 'presence' を含むVenue)の抽出
  - 標準出力: 照合段階別の件数、非完全一致が採否に影響した件数、
      指定略称(APGV/MIG/ICPS/ISMAR/VRST/SAP)の照合状況、Presence チェック

【方法(決定論的)】
  pipeline.py と同一の正規化・照合関数を import して照合段階を再現する。
  類似度は pipeline と同じ difflib.SequenceMatcher.ratio()(ファジー段階のみ)。

実行: python -X utf8 scripts/venue_match_audit.py
"""

from __future__ import annotations

import csv
import difflib
import sys
from collections import Counter, defaultdict
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
sys.path.insert(0, str(ROOT))

from pipeline import (  # noqa: E402
    HIGH_RANKS,
    extract_parenthesized_acronym,
    load_core,
    load_sjr,
    normalize_venue,
)

SUSPECT_SIM_MAX = 0.92   # ファジー照合でこれ以下の類似度は「疑い」として抽出
ACRONYM_CHECKLIST = ["APGV", "MIG", "ICPS", "ISMAR", "VRST", "SAP", "VR", "CHI"]


def classify_core_match(venue: str, core: dict):
    """pipeline.best_core_match と同じ優先順位で、どの段階で一致したかを返す。
    Returns (stage, matched_key, similarity) / stage in
    {exact_norm, exact_lower, acronym, fuzzy, none}"""
    norm = normalize_venue(venue)
    low = venue.strip().lower()
    if norm and norm in core:
        return "exact_norm", norm, 1.0
    if low in core:
        return "exact_lower", low, 1.0
    acr = extract_parenthesized_acronym(venue)
    if acr:
        if acr.lower() in core:
            return "acronym", acr.lower(), 1.0
        acr_norm = normalize_venue(acr)
        if acr_norm and acr_norm in core:
            return "acronym", acr_norm, 1.0
    # fuzzy(pipeline と同じ length-pruned SequenceMatcher)
    best_s, best_k = 0.0, None
    if norm:
        for k in core:
            m = max(len(norm), len(k))
            if m == 0 or abs(len(norm) - len(k)) > m * 0.18:
                continue
            s = difflib.SequenceMatcher(None, norm, k).ratio()
            if s > best_s:
                best_s, best_k = s, k
    if best_k and best_s >= 0.82:
        return "fuzzy", best_k, best_s
    return "none", None, 0.0


def classify_sjr_match(venue: str, issn: str, sjr: dict):
    """pipeline.best_sjr_match の段階再現。stage in {issn, exact_norm, exact_lower, none}"""
    import re
    issn_index = sjr.get("__issn_index__", {})
    for raw in re.split(r"[,\s]+", issn or ""):
        raw = raw.strip().replace("-", "")
        if raw and raw in issn_index:
            return "issn", raw, 1.0
    norm = normalize_venue(venue)
    low = venue.strip().lower()
    if norm and norm in sjr and norm != "__issn_index__":
        return "exact_norm", norm, 1.0
    if low in sjr and low != "__issn_index__":
        return "exact_lower", low, 1.0
    return "none", None, 0.0


def assign_priorities(rows_suspect: list[dict], core: dict, sjr: dict) -> None:
    """誤照合疑い行に著者目視の優先度を付す(決定論的)。

    - P1: 別の照合候補(類似度≥0.80)が存在し、その採否(A*/A/Q1 か圏外か)が
          現在の照合先と異なる = 照合先の選択が採否を変える
    - P2: 採否は変わらないが、元文字列同士の類似度 < 0.55 = 明らかに別会場の疑い
          (Presence型の「短い名前 × 積極的正規化」衝突はここで捕捉される)
    - P3: 上記以外 = 表記ゆれの範囲内と思われる
    """
    core_keys = list(core)
    sjr_keys = [k for k in sjr if k != "__issn_index__"]
    for rec in rows_suspect:
        raw = rec["raw_venue"]
        norm = normalize_venue(raw)
        cur_adopted = rec["decision"] == "INCLUDED"
        orig_sim = difflib.SequenceMatcher(
            None, raw.lower(), rec["matched_entry"].lower()).ratio()
        rec["orig_string_sim"] = f"{orig_sim:.3f}"
        rec["alt_candidate"] = ""
        priority = ""
        if norm:
            cands = (difflib.get_close_matches(norm, core_keys, n=5, cutoff=0.7)
                     + difflib.get_close_matches(norm, sjr_keys, n=5, cutoff=0.75))
            for k in cands:
                if k in core:
                    e = core[k]
                    alt_adopt = e["rank"] in HIGH_RANKS
                    name, rk = e["original_title"], f"CORE {e['rank']}"
                else:
                    e = sjr[k]
                    alt_adopt = e["quartile"] == "Q1"
                    name, rk = e["original_title"], f"SJR {e['quartile']}"
                if name == rec["matched_entry"]:
                    continue
                s = difflib.SequenceMatcher(None, norm, k).ratio()
                if s >= 0.80 and alt_adopt != cur_adopted:
                    rec["alt_candidate"] = (
                        f"{name} [{rk}] sim={s:.2f} "
                        f"({'採用側' if alt_adopt else '除外側'})")
                    priority = "P1"
                    break
        if not priority:
            priority = "P2" if orig_sim < 0.55 else "P3"
        rec["priority"] = priority


def main() -> None:
    core = load_core(ROOT / "CORE.csv")
    sjr = load_sjr(ROOT / "scimagojr 2025.csv")
    outdir = ROOT / "outputs"
    outdir.mkdir(exist_ok=True)

    # (raw_venue, matched, source, rank, decision) -> record count
    groups: dict[tuple, int] = Counter()
    issn_by_venue: dict[str, str] = {}
    for fname, decision in [("step2_rank_included.csv", "INCLUDED"),
                            ("step2_rank_excluded.csv", "EXCLUDED")]:
        with (ROOT / fname).open(encoding="utf-8-sig", newline="",
                                 errors="replace") as f:
            for row in csv.DictReader(f):
                mv = (row.get("Matched_Venue") or "").strip()
                if not mv:
                    continue  # 未照合は対象外(unmatched_venue_audit.py が担当)
                raw = (row.get("Publication Title") or "").strip()
                src = (row.get("Ranking_Source") or "").strip()
                rank = (row.get("CORE_Rank") or "").strip() or \
                       (row.get("SJR_Quartile") or "").strip()
                groups[(raw, mv, src, rank, decision)] += 1
                if raw not in issn_by_venue:
                    issn_by_venue[raw] = (row.get("ISSN") or "").strip()

    print(f"[INFO] 照合成功レコードのユニーク (raw venue × match × 採否): {len(groups):,}")

    rows_all, rows_suspect = [], []
    stage_counts: Counter[str] = Counter()
    nonexact_records = defaultdict(int)  # decision -> record count via non-exact
    for (raw, mv, src, rank, decision), n in sorted(groups.items(),
                                                    key=lambda x: -x[1]):
        if src == "CORE":
            stage, _, sim = classify_core_match(raw, core)
        else:
            stage, _, sim = classify_sjr_match(raw, issn_by_venue.get(raw, ""), sjr)
        stage_counts[f"{src}:{stage}"] += n
        if stage not in ("exact_norm", "exact_lower", "issn"):
            nonexact_records[decision] += n
        rec = {
            "raw_venue": raw, "matched_entry": mv, "source": src, "rank": rank,
            "match_stage": stage, "similarity": f"{sim:.3f}",
            "record_count": n, "decision": decision,
        }
        rows_all.append(rec)
        suspicious = (
            (stage == "fuzzy" and sim <= SUSPECT_SIM_MAX)
            or stage == "acronym"
            or "presence" in raw.lower()
            or stage == "none"  # 再現不能(照合ロジック変更等) — 要調査
        )
        if suspicious:
            rows_suspect.append(rec)

    fields = list(rows_all[0].keys())
    with (outdir / "venue_match_audit.csv").open("w", encoding="utf-8-sig",
                                                 newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows_all)

    # 著者目視の負担軽減: 優先度付け(P1: 採否が変わり得る / P2: 別会場疑い / P3: 表記ゆれ)
    print(f"\n[INFO] 誤照合疑い {len(rows_suspect)} 件に優先度を付与中(候補探索に数分)...")
    assign_priorities(rows_suspect, core, sjr)
    prio_order = {"P1": 0, "P2": 1, "P3": 2}
    rows_suspect.sort(key=lambda r: (prio_order.get(r["priority"], 9),
                                     -r["record_count"]))
    suspect_fields = fields + ["priority", "orig_string_sim", "alt_candidate"]
    with (outdir / "venue_suspect_matches.csv").open("w", encoding="utf-8-sig",
                                                     newline="") as f:
        w = csv.DictWriter(f, fieldnames=suspect_fields)
        w.writeheader()
        w.writerows(rows_suspect)
    p_counts = Counter(r["priority"] for r in rows_suspect)
    p_recs = defaultdict(int)
    for r in rows_suspect:
        p_recs[r["priority"]] += r["record_count"]
    print("  優先度別(ユニーク/レコード):")
    for p, label in [("P1", "採否が変わり得る照合(最優先で目視)"),
                     ("P2", "採否不変だが別会場の疑い"),
                     ("P3", "表記ゆれの範囲内と推定")]:
        print(f"    {p}: {p_counts.get(p, 0):>4} ユニーク / {p_recs.get(p, 0):>5,} "
              f"レコード — {label}")

    total = sum(groups.values())
    print()
    print("=" * 68)
    print("  照合段階別レコード数(照合成功側の全数)")
    print("=" * 68)
    for k, v in stage_counts.most_common():
        print(f"  {k:<22}: {v:>7,}")
    print(f"  {'合計':<22}: {total:>7,}")
    print()
    print("  非完全一致(acronym/fuzzy)による照合が採否に影響した件数:")
    for d in ("INCLUDED", "EXCLUDED"):
        print(f"    {d}: {nonexact_records.get(d, 0):,} 件")
    print()
    print(f"  誤照合疑い(suspect)      : {len(rows_suspect)} ユニーク / "
          f"{sum(r['record_count'] for r in rows_suspect):,} レコード"
          f" -> outputs/venue_suspect_matches.csv")

    # --- 明示チェック 1: 'Presence' を含む Venue ---
    print()
    print("=" * 68)
    print("  明示チェック: 'Presence' を含む Venue の照合先")
    print("=" * 68)
    hits = [r for r in rows_all if "presence" in r["raw_venue"].lower()]
    if not hits:
        print("  該当なし")
    for r in hits:
        print(f"  ({r['record_count']:>3}件/{r['decision']}) '{r['raw_venue']}'")
        print(f"      -> {r['matched_entry']} [{r['source']} {r['rank']}] "
              f"stage={r['match_stage']} sim={r['similarity']}")

    # --- 明示チェック 2: 略称の展開状況 ---
    print()
    print("=" * 68)
    print("  明示チェック: 略称を含む Venue の照合状況(照合成功側)")
    print("=" * 68)
    for acr in ACRONYM_CHECKLIST:
        matched = [r for r in rows_all
                   if f"({acr})" in r["raw_venue"] or f" {acr} " in f" {r['raw_venue']} "
                   or r["raw_venue"].upper().find(f"{acr} 20") >= 0]
        n = sum(r["record_count"] for r in matched)
        stages = Counter(r["match_stage"] for r in matched)
        print(f"  {acr:<6}: {len(matched):>3} ユニーク / {n:>5,} レコード "
              f"{dict(stages) if matched else '(照合成功側に出現なし → 未照合側を確認)'}")

    print()
    print("  ※ 未照合側の状況は unmatched_venue_audit.py / "
          "outputs/unmatched_venues_top50.csv を参照。")


if __name__ == "__main__":
    main()
