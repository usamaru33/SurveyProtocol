#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_calibration_supplement.py — 校正セット拡大の差分だけを補足シートにする
================================================================================

【何を】
校正セットの割合を引き上げたとき(Rev.22: 15% → 20%)、**新たに校正セットへ入った
文献だけ**を抜き出して `screening/supplement_sheet_<id>.csv` を出力する。

【なぜ差分なのか — 配布済みの判定を捨てないため】
校正セットの抽出は `md5("cal:"+key) % 100 < pct` で、**閾値について単調**である。
`< 15` の集合は `< 20` の集合に完全に含まれるため、割合を上げても
**既に校正セットだった文献が外れることはない**(実測: 外れ 0件 / 追加 59件)。

したがって既存シート(164件)を作り直す必要はなく、差分だけを追加すればよい。
既存シートを 223件で再生成して配り直すと、評価者が済ませた判定をやり直させることになる。

> **既存の `sheet_<id>.xlsx` は絶対に再生成しないこと。** 配布済みで記入が進行中である。
> 本スクリプトは既存シートを一切書き換えない。

【前提】
`make_screening_sheets.py` を新しい `CALIBRATION_PCT` で実行し、`assignment.csv` が
更新済みであること。既存の `sheet_<id>.csv` は旧割合のまま残っていてよい
(そちらに載っている文献は引き続き校正セットである)。

【入出力】
  入力: screening/assignment.csv        (新しい割合で再生成済み)
        screening/sheet_<id>.csv        (配布済み。どの文献が既出かの判定に使う)
  出力: screening/supplement_sheet_<id>.csv

続けて Excel 版を作る:
  python -X utf8 scripts/make_screening_xlsx.py --prefix supplement_

実行:
  python -X utf8 scripts/make_calibration_supplement.py
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

from make_screening_sheets import REVIEWERS, SHEET_COLS  # noqa: E402


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        return list(csv.DictReader(f))


def main() -> None:
    ap = argparse.ArgumentParser(description="校正セット拡大の差分を補足シートにする")
    ap.add_argument("--dir", type=Path, default=ROOT / "screening")
    ap.add_argument("--force", action="store_true", help="既存の補足シートを上書きする")
    args = ap.parse_args()

    apath = args.dir / "assignment.csv"
    if not apath.exists():
        sys.exit("[ERROR] assignment.csv が無い。先に make_screening_sheets.py を実行すること")

    assignment = load(apath)
    cal_now = {r["record_id"] for r in assignment if r.get("calibration") == "Y"}

    # 著者は全件を判定済みなので補足は不要。第2評価者2名だけが対象。
    targets = [r for r in REVIEWERS if r != "author"]

    for rev in targets:
        existing_path = args.dir / f"sheet_{rev}.csv"
        if not existing_path.exists():
            sys.exit(f"[ERROR] {existing_path.name} が無い。配布済みシートが必要")
        already = {r["record_id"] for r in load(existing_path)}

        add_ids = cal_now - already
        if not add_ids:
            print(f"[SKIP] {rev}: 追加分なし(既に {len(already)} 件で校正セットを網羅)")
            continue

        # 補足シートの行は「判定対象の全件シート」から引く。
        # 著者シートは全1,052件を含むため、ここから該当行を取り出せる。
        src = load(args.dir / "sheet_author.csv")
        rows = [r for r in src if r["record_id"] in add_ids]
        if len(rows) != len(add_ids):
            sys.exit(f"[ERROR] {rev}: 追加対象 {len(add_ids)} 件のうち "
                     f"{len(rows)} 件しか見つからない")

        # 記入列は空にする(著者の判定を見せない。独立性の担保)
        for r in rows:
            r["decision"] = r["reason"] = r["note"] = ""

        # 既存シートと同じ並び(概念群の降順 → 新しい年順)にそろえる
        def sort_key(r):
            try:
                kw = -int(r.get("kw_groups") or 0)
            except ValueError:
                kw = 0
            try:
                yr = -int(float(r.get("year") or 0))
            except ValueError:
                yr = 0
            return (kw, yr, r["record_id"])
        rows.sort(key=sort_key)

        out = args.dir / f"supplement_sheet_{rev}.csv"
        if out.exists() and not args.force:
            print(f"[SKIP] {out.name} は既にある(上書きするなら --force)")
            continue
        with out.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=SHEET_COLS, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

        no_abs = sum(1 for r in rows if r.get("has_abstract") == "N")
        print(f"[INFO] 出力: {out.name}  {len(rows)} 件  担当={REVIEWERS[rev]}"
              f"  (うち要旨なし {no_abs} 件)")
        print(f"       既存 {len(already)} 件 + 追加 {len(rows)} 件 = {len(already)+len(rows)} 件")

    print("\n[NEXT] Excel 版を作る:")
    print("       python -X utf8 scripts/make_screening_xlsx.py --prefix supplement_")
    print("       **既存の sheet_<id>.xlsx は再生成しないこと**(配布済み・記入進行中)")


if __name__ == "__main__":
    main()
