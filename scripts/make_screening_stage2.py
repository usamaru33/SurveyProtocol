#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_screening_stage2.py — liberal accelerated の stage 2 判定シートを生成する
================================================================================

【何を】
著者が stage 1(全1,052件)の判定を終えたあと、**著者が Exclude にしたレコードだけ**を
第2評価者(Kataoka / WATANABE)に配るシートを生成する。

【なぜ Exclude だけなのか — liberal accelerated】
「1人が Include にすれば通す。Exclude するには2人必要」。Phase 3b のエラーは非対称で、
誤って Exclude すると全文を読む機会が永久に失われる(回復不能)が、誤って Include しても
Phase 4 の手間が増えるだけである。**除外の方向にだけ2人を要求する**ことで、
工数を抑えつつ感度を2人体制と同等に保つ。

単独スクリーニングは関連文献の 13% を見落とす(2人体制は 3%)という RCT の実測があり、
本方式はその差を除外側の二重化で埋める設計である。

【校正セットは対象外】
校正セット(`calibration=Y`、3名全員が stage 1 で全判定済み)は既に二重化されているので
stage 2 では配らない。κ はこの校正セットで算出する
(除外プールだけでは著者の判定に分散が無く κ が常に 0 になるため)。

【入出力】
  入力: screening/assignment.csv, screening/sheet_author.(xlsx|csv)
  出力: screening/stage2_sheet_<id>.csv / .xlsx

実行:
  python -X utf8 scripts/make_screening_stage2.py
  python -X utf8 scripts/make_screening_stage2.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(_HERE))

csv.field_size_limit(10 ** 9)

from make_screening_sheets import REVIEWERS, SHEET_COLS, second_reviewer_of  # noqa: E402
from score_screening import load_sheet  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="liberal accelerated の stage 2 シート生成")
    ap.add_argument("--dir", type=Path, default=ROOT / "screening")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    apath = args.dir / "assignment.csv"
    if not apath.exists():
        sys.exit(f"[ERROR] {apath} がありません")
    with apath.open(encoding="utf-8-sig", newline="") as f:
        assignment = {r["record_id"]: r for r in csv.DictReader(f)}

    author = load_sheet(args.dir / "sheet_author.csv")
    if not author:
        sys.exit("[ERROR] 著者の判定シートが読めません")

    blank = sum(1 for r in author.values() if not (r.get("decision") or "").strip())
    if blank:
        sys.exit(f"[ERROR] 著者シートに未記入が {blank:,} 件あります。"
                 f"stage 1 を完了してから実行すること")

    per: dict[str, list[dict]] = {r: [] for r in REVIEWERS if r != "author"}
    n_inc = n_exc = n_unsure = n_cal = 0
    for rid, row in author.items():
        a = assignment.get(rid)
        if not a:
            continue
        d = (row.get("decision") or "").strip().lower()
        if a.get("calibration") == "Y":
            n_cal += 1
            continue                      # 校正セットは stage 1 で二重化済み
        if d == "include":
            n_inc += 1
            continue                      # Include は1人で通す(liberal accelerated)
        if d == "unsure":
            n_unsure += 1                 # Unsure も第2評価者へ回す(協議の材料)
        else:
            n_exc += 1
        rv = second_reviewer_of(a["key"])
        fresh = {k: row.get(k, "") for k in SHEET_COLS}
        fresh["decision"] = fresh["reason"] = fresh["note"] = ""   # 著者の判定は見せない
        per[rv].append(fresh)

    print(f"[INFO] 著者の stage 1 判定: {len(author):,} 件")
    print(f"       校正セット(二重化済み・対象外)   : {n_cal:,}")
    print(f"       Include(1人で通す・対象外)       : {n_inc:,}")
    print(f"       Exclude(第2評価者へ)             : {n_exc:,}")
    print(f"       Unsure(第2評価者へ)              : {n_unsure:,}")
    for r, lst in per.items():
        lst.sort(key=lambda x: (-int(x.get("kw_groups") or 0), x.get("record_id", "")))
        print(f"    {REVIEWERS[r]:18s}: {len(lst):5,d} 件")

    if args.dry_run:
        print("\n[DRY-RUN] ファイルは書き込んでいない。")
        return

    for r, lst in per.items():
        p = args.dir / f"stage2_sheet_{r}.csv"
        if p.exists():
            print(f"[SKIP] {p.name} は既にある(記入済みを壊さないため生成しない)")
            continue
        with p.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=SHEET_COLS, extrasaction="ignore")
            w.writeheader()
            w.writerows(lst)
        print(f"[INFO] 出力: {p.name}  ({len(lst):,} 行)  担当={REVIEWERS[r]}")

    print("\n[NEXT] Excel 版は "
          "`python -X utf8 scripts/make_screening_xlsx.py --prefix stage2_` で作る。")
    print("       ★ 第2評価者に**著者の判定は見せない**(独立性の担保。列は空にしてある)。")


if __name__ == "__main__":
    main()
