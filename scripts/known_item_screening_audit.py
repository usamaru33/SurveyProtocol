#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
known_item_screening_audit.py — Known-Item が Phase 3b の判定対象に残ったかを照合する
================================================================================

【何を】
`known_item_test.py` はパイプラインの step ファイル(DB検索側)だけを対象にしており、
**引用探索(スノーボーリング)で回収された分を勘定に入れていない**。
本スクリプトは Phase 3b の判定対象 1,052件(= DB検索 795 + 引用探索 257)に対して
gold set の in-scope 文献が何件残ったかを照合し、取得経路の内訳を出す。

【なぜ要るか】
スノーボーリングの目的(A)は「Venue フィルタで脱落した Known-Item の回収」だった
(`docs/snowballing_protocol.md` §0)。その**実測値**が無いと、Threats to Validity で
「検索式のギャップを引用探索で補完した」と書けない。

【読み取り専用】
判定シートも step ファイルも一切書き換えない。Phase 3b の凍結(Rev.19)の対象外。
出力は `outputs/known_item_in_screening.csv` のみ。

【照合方法】
DOI の正規化一致を第一とし、DOI が無い/一致しない場合のみ正規化タイトル一致で補う。
いずれも決定論的で、ファジー一致は使わない(recall を過大に見せないため)。

実行:
  python -X utf8 scripts/known_item_screening_audit.py
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(_HERE))

csv.field_size_limit(10 ** 9)

from make_screening_sheets import norm_doi  # noqa: E402

GOLD = ROOT / "self_scale_references.csv"
SHEET = ROOT / "screening" / "sheet_author.csv"   # 判定対象の全件(1,052)
OUT = ROOT / "outputs" / "known_item_in_screening.csv"


def norm_title(t: str) -> str:
    """英数字だけを残して比較する。句読点・空白・大小文字の揺れを吸収する。"""
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def main() -> None:
    if not SHEET.exists():
        sys.exit(f"[ERROR] {SHEET.name} が無い。先に make_screening_sheets.py を実行すること")

    with GOLD.open(encoding="utf-8-sig", newline="") as f:
        gold = [r for r in csv.DictReader(f) if r.get("SearchScope") == "in-scope"]
    with SHEET.open(encoding="utf-8-sig", newline="") as f:
        target = list(csv.DictReader(f))

    by_doi = {norm_doi(r.get("doi", "")): r for r in target if norm_doi(r.get("doi", ""))}
    by_title = {norm_title(r.get("title", "")): r for r in target}
    calibration = {r["record_id"] for r in target if r.get("calibration") == "Y"}

    rows = []
    for g in sorted(gold, key=lambda r: (r.get("Year", ""), r.get("Title", ""))):
        doi = norm_doi(g.get("DOI_or_URL", ""))
        rec, how = (by_doi.get(doi), "DOI") if doi and doi in by_doi else (None, "")
        if rec is None:
            rec = by_title.get(norm_title(g.get("Title", "")))
            how = "title" if rec else "—"
        rows.append({
            "year": g.get("Year", ""),
            "title": g.get("Title", ""),
            "venue": g.get("Venue", ""),
            "doi": g.get("DOI_or_URL", ""),
            "in_screening": "Y" if rec else "N",
            "match_method": how,
            "source": rec.get("source", "") if rec else "",
            "record_id": rec.get("record_id", "") if rec else "",
            "calibration": ("Y" if rec and rec["record_id"] in calibration else "N") if rec else "",
            "has_abstract": rec.get("has_abstract", "") if rec else "",
            "intervention_modality": g.get("InterventionModality", ""),
            "evaluation_target": g.get("EvaluationTarget", ""),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    hit = [r for r in rows if r["in_screening"] == "Y"]
    by_source = Counter(r["source"] for r in hit)
    in_cal = sum(1 for r in hit if r["calibration"] == "Y")
    n = len(rows)

    print("=" * 70)
    print("  Known-Item(in-scope)が Phase 3b の判定対象に残ったか")
    print("=" * 70)
    print(f"  gold set in-scope        : {n} 件")
    print(f"  判定対象に含まれる        : {len(hit)}/{n}  ({len(hit) / n * 100:.1f}%)")
    for src, c in sorted(by_source.items()):
        print(f"      {src:<14}: {c}")
    print(f"  うち校正セット(κ算出用)   : {in_cal}")
    print()
    print("  ※ known_item_test.py の step3 recall は DB検索側(795件)のみを対象にしており、")
    print("     引用探索で回収された分を含まない。両者の差が引用探索の寄与にあたる。")
    print(f"\n[INFO] 出力: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
