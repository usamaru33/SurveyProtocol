#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
unmatched_venue_audit.py — Phase 2 Venue未照合 5,126件の実態調査
================================================================================

【何を】
Phase 2(Venueランクスクリーニング)で「CORE/SJR いずれにも照合できず」除外された
レコード群(Excl_Reason_Phase2 = "Venue not found in CORE or SJR")について、
Venue名を出現頻度順に集計し、上位50件それぞれに対して CORE / SJR リスト内の
Levenshtein 最近傍(表記ゆれの疑い先)とそのランクを併記した監査表を出力する。

【なぜ】
未照合 5,126件を一括除外している現行処理の妥当性を検証するため。
「表記ゆれのせいで落ちた実質 A*/A/Q1 Venue」がどれだけ存在するかを目視判断できる
形にし、除外の妥当性(あるいは救済の必要性)を論文の Threats to Validity 節に
証拠として記載する。既存の step1〜3 出力は一切変更しない(読み取り専用)。

【入力】
  - step2_rank_excluded.csv   Phase 2 除外レコード(Excl_Reason_Phase2 列で絞り込み)
  - CORE.csv                  CORE 学会ランキング
  - scimagojr 2025.csv        SJR ジャーナルランキング

【出力】
  - outputs/unmatched_venues_top50.csv
      freq_rank, venue_raw, record_count, venue_norm,
      core_nn_title, core_nn_rank, core_nn_lev_sim,
      sjr_nn_title, sjr_nn_quartile, sjr_nn_lev_sim,
      flag_potential_highrank_miss(lev≥0.85 かつ A*/A/Q1 → 要目視確認),
      flag_q2_neighbor(lev≥0.85 かつ Q2 → rule.md「不足時Q2」判断の材料)
  - 標準出力: 件数サマリ(top50 のカバレッジ、フラグ件数)

【方法(決定論的)】
  Venue名は pipeline.py と同一の normalize_venue() で正規化。
  最近傍探索は difflib による候補絞り込み(上位5件)→ Levenshtein 類似度
  (1 - 編集距離/最大長)で再ランクし最良を採択。乱数・外部API・AI 判定は不使用。

実行: python -X utf8 scripts/unmatched_venue_audit.py
"""

from __future__ import annotations

import csv
import difflib
import sys
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent  # SurveyProtocol/
sys.path.insert(0, str(ROOT))

# 本番と同じ正規化・ローダを使う(検証と本番の基準乖離を防ぐ)
from pipeline import load_core, load_sjr, normalize_venue  # noqa: E402

TOP_N = 50
SIM_FLAG_THRESHOLD = 0.85  # この類似度以上の最近傍は「実質同一の疑い」として旗を立てる
HIGH_RANKS = {"A*", "A"}


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a or not b:
        return max(len(a), len(b))
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def lev_sim(a: str, b: str) -> float:
    m = max(len(a), len(b))
    return 1.0 if m == 0 else 1 - levenshtein(a, b) / m


def nearest(norm: str, keys: list[str], entries: dict, cutoff: float):
    """difflib で候補を絞り、Levenshtein 類似度で再ランクして最良1件を返す。"""
    if not norm:
        return "", "", 0.0
    cands = difflib.get_close_matches(norm, keys, n=5, cutoff=cutoff)
    best_key, best_sim = "", 0.0
    for k in cands:
        s = lev_sim(norm, k)
        if s > best_sim:
            best_key, best_sim = k, s
    if not best_key:
        return "", "", 0.0
    return entries[best_key][0], entries[best_key][1], best_sim


def main() -> None:
    excl_path = ROOT / "step2_rank_excluded.csv"
    outdir = ROOT / "outputs"
    outdir.mkdir(exist_ok=True)
    out_csv = outdir / "unmatched_venues_top50.csv"

    # --- 未照合レコードの Venue 集計 ---
    counter: Counter[str] = Counter()
    total_unmatched = 0
    with excl_path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        for row in csv.DictReader(f):
            if (row.get("Excl_Reason_Phase2") or "").strip() != \
                    "Venue not found in CORE or SJR":
                continue
            total_unmatched += 1
            venue = (row.get("Publication Title") or "").strip()
            counter[venue if venue else "(空欄)"] += 1

    print(f"[INFO] Venue未照合レコード: {total_unmatched:,} 件 / "
          f"ユニークVenue名: {len(counter):,} 種")

    # --- ランキングリストの索引(正規化キー → (原題, ランク)) ---
    core_raw = load_core(ROOT / "CORE.csv")
    core_entries = {k: (v["original_title"], v["rank"]) for k, v in core_raw.items()}
    core_keys = list(core_entries)

    sjr_raw = load_sjr(ROOT / "scimagojr 2025.csv")
    sjr_entries = {k: (v["original_title"], v["quartile"])
                   for k, v in sjr_raw.items() if k != "__issn_index__"}
    sjr_keys = list(sjr_entries)
    print(f"[INFO] 照合先: CORE {len(core_keys):,} キー / SJR {len(sjr_keys):,} キー")
    print(f"[INFO] 上位 {TOP_N} Venue の最近傍を探索中(SJR 5万件のため数分かかる)...")

    top = counter.most_common(TOP_N)
    covered = sum(c for _, c in top)

    rows_out = []
    n_highrank = 0
    n_q2 = 0
    for i, (venue, count) in enumerate(top, 1):
        norm = normalize_venue(venue) if venue != "(空欄)" else ""
        c_title, c_rank, c_sim = nearest(norm, core_keys, core_entries, cutoff=0.5)
        s_title, s_q, s_sim = nearest(norm, sjr_keys, sjr_entries, cutoff=0.6)

        flag_high = "Y" if ((c_sim >= SIM_FLAG_THRESHOLD and c_rank in HIGH_RANKS)
                            or (s_sim >= SIM_FLAG_THRESHOLD and s_q == "Q1")) else ""
        flag_q2 = "Y" if (s_sim >= SIM_FLAG_THRESHOLD and s_q == "Q2") else ""
        n_highrank += flag_high == "Y"
        n_q2 += flag_q2 == "Y"

        rows_out.append({
            "freq_rank": i,
            "venue_raw": venue,
            "record_count": count,
            "venue_norm": norm,
            "core_nn_title": c_title,
            "core_nn_rank": c_rank,
            "core_nn_lev_sim": f"{c_sim:.3f}" if c_title else "",
            "sjr_nn_title": s_title,
            "sjr_nn_quartile": s_q,
            "sjr_nn_lev_sim": f"{s_sim:.3f}" if s_title else "",
            "flag_potential_highrank_miss": flag_high,
            "flag_q2_neighbor": flag_q2,
        })
        print(f"  [{i:>2}/{TOP_N}] ({count:>4}件) {venue[:60]}")

    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)

    print()
    print("=" * 64)
    print("  Unmatched Venue Audit — サマリ")
    print("=" * 64)
    print(f"  未照合レコード総数            : {total_unmatched:>7,}")
    print(f"  ユニークVenue名               : {len(counter):>7,}")
    print(f"  上位{TOP_N}Venueのレコード数     : {covered:>7,} "
          f"({covered / total_unmatched:.1%} をカバー)")
    print(f"  高ランク(A*/A/Q1)近傍フラグ  : {n_highrank:>7} 件  ← 要目視確認(取りこぼし疑い)")
    print(f"  Q2 近傍フラグ                : {n_q2:>7} 件  ← rule.md「不足時Q2」判断の材料")
    print(f"\n  出力: {out_csv}")
    print("  ※ フラグ行を目視し、実質同一Venueと判断した場合の扱い(救済/除外維持)を"
          "PROGRESS_LOG.md に記録すること。")


if __name__ == "__main__":
    main()
