#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_raw.py — raw/ の DB別エクスポートから統合生データを組み立てる
================================================================================

【何を】
`raw/*.csv`(Zotero のコレクション別エクスポート)を連結し、
**取得元DBを示す `Source_DB` 列を付与**した統合生データ(既定 `ResearchVR4.csv`)を作る。
重複削除は**行わない**(それは `pipeline.py` の Phase 1 の責務)。

【なぜ】
現行の統合データ `ResearchVR2.csv` / `ResearchVR3.csv` が**どう作られたかの記録が無く**、
再現できないことが Rev.7 の検証で問題になった。加えて `search_replication.md`
「重複ID列の扱い(統合時)」が「取得元DB列を追加してから統合する(統合後は復元不能)」と
要求しているのに、既存の統合CSVには取得元DB列が無く、URL/DOI からの**推定**に頼っていた
(README §7 タスク2 の DB別集計が推定ベースなのはこのため)。
統合をコード化してこの2点を同時に解消する。

【PubMed の扱い】
**既定で除外する。** Rev.8 で「医学・治療目的の文献はスコープ外・主題適合性が低い」として
DB構成を3DB(ACM/IEEE/Scopus)に確定したため、PRISMA の "records identified" に
PubMed を含めてはならない。初回検索データ `raw/PubMed.csv` は経緯として保存してあるので、
参考集計が必要なときだけ `--include-pubmed` で明示的に含める。

【入力】
  - raw/*.csv    Zotero コレクション別エクスポート(ファイル名が取得元DBの記録を兼ねる)

【出力】
  - ResearchVR4.csv (既定)   統合生データ + Source_DB 列
    ※ `scripts/known_item_test.py` は `ResearchVR*.csv` の名前昇順で最後を step0 に使うため、
      このファイルを置くだけで Known-Item Test の対象が自動的に最新版に切り替わる。

【方法(決定論的)】
  行の加工は Source_DB 列の付与のみ。並び順は入力ファイル名の昇順 → ファイル内の元の順序。
  乱数・外部API・AI 判定は不使用。

実行例:
  python -X utf8 scripts/merge_raw.py --dry-run     # 件数の内訳だけ表示
  python -X utf8 scripts/merge_raw.py               # ResearchVR4.csv を生成
  python -X utf8 scripts/merge_raw.py --include-pubmed --out ResearchVR4_with_pubmed.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
RAW_DIR = ROOT / "raw"

SOURCE_COL = "Source_DB"

# ファイル名(小文字)の接頭辞 → Source_DB の値。第2波は波の別も残す。
SOURCE_RULES = [
    ("acm_wave2", "ACM(wave2)"),
    ("acm", "ACM"),
    ("ieee_wave2", "IEEE(wave2)"),
    ("ieee_2025-2026", "IEEE(update)"),
    ("ieee", "IEEE"),
    ("scopus_wave2", "Scopus(wave2)"),
    ("scopus", "Scopus"),
    ("pubmed", "PubMed"),
]


def source_of(path: Path) -> str:
    n = path.stem.lower()
    for prefix, label in SOURCE_RULES:
        if n.startswith(prefix):
            return label
    return path.stem


def load(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        r = csv.DictReader(f)
        return (r.fieldnames or []), list(r)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="raw/*.csv を連結して統合生データを作る(重複削除はしない)")
    ap.add_argument("--out", type=Path, default=ROOT / "ResearchVR4.csv")
    ap.add_argument("--include-pubmed", action="store_true",
                    help="PubMed を含める(既定は Rev.8 により除外)")
    ap.add_argument("--dry-run", action="store_true",
                    help="ファイルを書かず、件数の内訳だけ表示する")
    args = ap.parse_args()

    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        sys.exit(f"[ERROR] {RAW_DIR} に CSV がありません")

    used, skipped = [], []
    for p in files:
        if source_of(p) == "PubMed" and not args.include_pubmed:
            skipped.append(p)
        else:
            used.append(p)

    # --- スキーマの確認(列構成が違うファイルがあれば和集合を取る) ---
    all_fields: list[str] = []
    per_file: list[tuple[Path, list[str], list[dict]]] = []
    for p in used:
        fields, rows = load(p)
        per_file.append((p, fields, rows))
        for c in fields:
            if c not in all_fields:
                all_fields.append(c)

    schema_uniform = all(fields == per_file[0][1] for _, fields, _ in per_file)
    if not schema_uniform:
        print("[WARN] 列構成がファイル間で一致しません。列の和集合を取り、"
              "欠けている列は空文字で埋めます。")
        for p, fields, _ in per_file:
            missing = [c for c in all_fields if c not in fields]
            if missing:
                print(f"    {p.name}: 欠落 {len(missing)} 列 (例: {missing[:3]})")

    if SOURCE_COL in all_fields:
        sys.exit(f"[ERROR] 入力に既に '{SOURCE_COL}' 列があります。"
                 f"二重付与を避けるため中断します。")
    out_fields = all_fields + [SOURCE_COL]

    print(f"[INFO] 統合対象 {len(used)} ファイル / 列数 {len(out_fields)}"
          f"({SOURCE_COL} を含む)")
    if skipped:
        print(f"[INFO] 除外: {', '.join(p.name for p in skipped)} "
              f"(Rev.8 により PubMed は不使用。含めるには --include-pubmed)")

    merged: list[dict] = []
    print("\n  取得元別の内訳:")
    for p, _fields, rows in per_file:
        src = source_of(p)
        for r in rows:
            row = {c: r.get(c, "") for c in all_fields}
            row[SOURCE_COL] = src
            merged.append(row)
        print(f"    {src:<15} {p.name:<32} {len(rows):>7,} 件")
    print(f"    {'合計':<15} {'':<32} {len(merged):>7,} 件"
          f"  ※ DB間重複を含む。Phase 1 で削除される")

    if args.dry_run:
        print("\n[DRY-RUN] ファイルは書き込んでいません。")
        return

    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        w.writerows(merged)
    print(f"\n[INFO] 出力: {args.out}  ({len(merged):,} 件)")
    print("[NEXT] パイプラインへの投入は "
          f"`python -X utf8 pipeline.py --input {args.out.name}`。")
    print("       ただし step ファイルは凍結中のため、公式再実行のタイミングは "
          "docs/PROGRESS_LOG.md の方針に従うこと。")


if __name__ == "__main__":
    main()
