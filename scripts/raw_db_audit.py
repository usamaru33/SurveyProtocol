#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
raw_db_audit.py — DB別生データ(raw/)の監査と PRISMA 上段数値の確定
================================================================================

【何を】
Zotero のDB別コレクションからエクスポートされた raw/*.csv について、
(1) DB別レコード数(= PRISMA "Records identified from each database")、
(2) 取り込み日(Date Added)の分布、
(3) 統合エクスポート ResearchVR2.csv との整合(Key 照合)、
(4) DB間重複(DOI / 正規化タイトルの一致)
を集計する。

【なぜ】
PRISMA 2020 フロー図の上段(identification)を、再検索なしに Zotero 実データから
確定するため。またDB間重複数は "Duplicate records removed" の内訳報告に使う。

【入力】
  - raw/*.csv           Zotero コレクション別エクスポート(ファイル名 = DB名)
  - ResearchVR2.csv     統合エクスポート(14,385件)

【出力】
  - outputs/raw_db_audit.csv   DB別: レコード数・Date Added 内訳・統合CSVとのKey一致数
  - 標準出力                    上記+DB間重複マトリクス+検証結果サマリ

【方法(決定論的)】
  Key(Zotero item key)で統合CSVと照合。DB間重複は DOI(正規化)一致を第一、
  DOI欠損対は正規化タイトル一致で補完。乱数・外部API・AI 判定は不使用。

実行: python -X utf8 scripts/raw_db_audit.py
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
RAW_DIR = ROOT / "raw"
MERGED = ROOT / "ResearchVR2.csv"


def norm_doi(raw: str) -> str:
    d = (raw or "").strip().lower()
    d = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", d)
    return re.sub(r"^doi:\s*", "", d)


def norm_title(raw: str) -> str:
    t = re.sub(r"[^a-z0-9]+", " ", (raw or "").lower())
    return re.sub(r"\s+", " ", t).strip()


def load(path: Path):
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        return list(csv.DictReader(f))


def main() -> None:
    raw_files = sorted(RAW_DIR.glob("*.csv"))
    if not raw_files:
        sys.exit(f"[ERROR] {RAW_DIR} に CSV がありません")

    merged = load(MERGED)
    merged_keys = {(r.get("Key") or "").strip() for r in merged}
    print(f"[INFO] 統合CSV: {len(merged):,} 件 / raw ファイル: "
          f"{', '.join(p.name for p in raw_files)}")

    dbs: dict[str, list[dict]] = {}
    rows_out = []
    total_raw = 0
    all_raw_keys: Counter[str] = Counter()

    print()
    print("=" * 72)
    print("  DB別集計(PRISMA: Records identified from each database)")
    print("=" * 72)
    for p in raw_files:
        db = p.stem
        rows = load(p)
        dbs[db] = rows
        total_raw += len(rows)
        dates = Counter((r.get("Date Added") or "")[:10] for r in rows)
        keys = [(r.get("Key") or "").strip() for r in rows]
        all_raw_keys.update(k for k in keys if k)
        in_merged = sum(1 for k in keys if k and k in merged_keys)
        doi_n = sum(1 for r in rows if norm_doi(r.get("DOI", "")))
        date_str = ", ".join(f"{d}: {n:,}" for d, n in sorted(dates.items()))
        print(f"  {db:<10}: {len(rows):>6,} 件 | 統合CSVとKey一致 {in_merged:>6,} "
              f"| DOIあり {doi_n:>6,} | Date Added [{date_str}]")
        rows_out.append({
            "db": db, "records": len(rows), "keys_in_merged": in_merged,
            "with_doi": doi_n, "date_added_breakdown": date_str,
        })

    print(f"  {'合計':<10}: {total_raw:>6,} 件  (統合CSV: {len(merged):,} 件)")

    # --- 整合検証 ---
    print()
    print("=" * 72)
    print("  整合検証(raw ⇔ 統合CSV)")
    print("=" * 72)
    dup_keys_within = {k: c for k, c in all_raw_keys.items() if c > 1}
    missing_in_merged = [k for k in all_raw_keys if k not in merged_keys]
    raw_key_set = set(all_raw_keys)
    merged_not_in_raw = [k for k in merged_keys if k and k not in raw_key_set]
    print(f"  raw 4ファイル合計とKeyユニーク数     : {total_raw:,} / {len(all_raw_keys):,}"
          f"(複数コレクション所属 {len(dup_keys_within):,} 件)")
    print(f"  raw にあり統合CSVに無い Key           : {len(missing_in_merged):,} 件")
    print(f"  統合CSVにあり raw のどこにも無い Key  : {len(merged_not_in_raw):,} 件")

    # --- DB間重複(DOI優先・タイトル補完) ---
    print()
    print("=" * 72)
    print("  DB間重複(同一文献が複数DBでヒット)— PRISMA重複除去の内訳用")
    print("=" * 72)
    ids: dict[str, set[str]] = {}
    for db, rows in dbs.items():
        s = set()
        for r in rows:
            d = norm_doi(r.get("DOI", ""))
            s.add("doi:" + d if d else "title:" + norm_title(r.get("Title", "")))
        ids[db] = s
    for a, b in combinations(sorted(dbs), 2):
        inter = ids[a] & ids[b]
        print(f"  {a:<10} ∩ {b:<10}: {len(inter):>5,} 件")

    outdir = ROOT / "outputs"
    outdir.mkdir(exist_ok=True)
    out_csv = outdir / "raw_db_audit.csv"
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)
    print(f"\n  出力: {out_csv}")


if __name__ == "__main__":
    main()
