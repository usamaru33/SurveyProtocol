#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
venue_dropped_audit.py — Venue フィルタ(step2)で脱落した Known-Item の整理
================================================================================

【何を】
methodology_decision_Rev7.md の最重要発見(known-item 13件中 6件が step2 =
Venue ホワイトリスト(CORE A*/A + SJR Q1)で脱落)を、スノーボーリング回収の
対象リストとして `outputs/venue_dropped_known_items.csv` に整理する。

【なぜ】
step2 脱落は「検索式の問題」でも「DB構成の問題」でもなく Venue 品質フィルタの
学際会場取りこぼしである。各件を回収方針(基準どおりの除外 / 照合漏れ /
学際会場未収載)で分類し、snowballing_protocol.md の入力にする。

【入力】
  outputs/known_item_test.csv   drop_stage == 'step2' の行を対象
【出力】
  outputs/venue_dropped_known_items.csv
    列: #, Title, Venue_expected, drop_reason, drop_category, recovery_action

【分類ルール(drop_reason 文字列からの決定論的判定)】
  - "SJR 'Q2'"（等 Q2 以下）を含む     → 'criterion'（基準どおりの除外。Threats で報告）
  - "未照合" を含む                    → 'unmatched'（照合漏れ or 会場がリスト未収載）
  - "CORE Rank 'C'"（等 A 未満）を含む → 'below_rank'（会場はリストに在るがランク不足）
  - それ以外                            → 'other'
  drop_category ごとの recovery_action:
    criterion  → 'keep excluded; report in Threats to Validity'
    unmatched  → 'check alias/normalization; if truly unlisted → snowballing'
    below_rank → 'keep excluded (quality criterion); recover cited-by via snowballing'
    other      → 'manual review'

実行: python -X utf8 scripts/venue_dropped_audit.py
"""

from __future__ import annotations

import csv
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
SRC = ROOT / "outputs" / "known_item_test.csv"
OUT = ROOT / "outputs" / "venue_dropped_known_items.csv"


def classify(reason: str) -> tuple[str, str]:
    r = reason or ""
    if "SJR 'Q2'" in r or "SJR 'Q3'" in r or "SJR 'Q4'" in r:
        return "criterion", "keep excluded; report in Threats to Validity"
    if "未照合" in r:
        return "unmatched", "check alias/normalization; if truly unlisted -> snowballing"
    if "CORE Rank 'C'" in r or "CORE Rank 'B'" in r or "CORE Rank 'D'" in r:
        return "below_rank", "keep excluded (quality criterion); recover cited-by via snowballing"
    return "other", "manual review"


def main() -> None:
    with SRC.open(encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("drop_stage") == "step2"]

    fields = ["#", "Title", "Venue_expected", "drop_reason",
              "drop_category", "recovery_action"]
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        counts: dict[str, int] = {}
        for r in rows:
            cat, action = classify(r.get("drop_reason", ""))
            counts[cat] = counts.get(cat, 0) + 1
            w.writerow({
                "#": r.get("#", ""),
                "Title": r.get("Title", ""),
                "Venue_expected": r.get("Venue_expected", ""),
                "drop_reason": r.get("drop_reason", ""),
                "drop_category": cat,
                "recovery_action": action,
            })
    print(f"[INFO] step2 脱落 known-item: {len(rows)} 件 -> {OUT}")
    for cat, n in sorted(counts.items()):
        print(f"    {cat}: {n}")


if __name__ == "__main__":
    main()
