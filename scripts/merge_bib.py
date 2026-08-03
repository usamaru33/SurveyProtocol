#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_bib.py — 分割エクスポートされた .bib を1本に統合する
================================================================================

【何を】
ディレクトリ内の `*.bib`(年スライスごとに分割エクスポートされたもの)を読み、
**引用キー単位で重複を除いて**1本の .bib に連結する。

【なぜ】
ACM DL のエクスポートは1回1,000件が上限のため、`search_replication.md` §1 の手順で
出版年ごとにスライスして複数回エクスポートする運用になっている。加えて title 検索と
abstract 検索を別々に実行して和集合を取るため(Rev.9 時点の決定)、同じ論文が
複数ファイルに現れる。BibTeX は**引用キーが重複すると取り込み側で警告・欠落が起きる**ので、
Zotero へ入れる前にキー単位で一意化しておく。

ACM の .bib は引用キーが DOI(例 `@inproceedings{10.1145/3424636.3426908,`)なので、
キーの一意化はそのまま DOI による重複除去になる。

【方針】
- **エントリ本文は一切加工しない**(先に現れたものをそのまま採用する)。
- 重複除去は「同じ論文を2回入れない」ためだけのもので、**スクリーニング上の重複削除
  (Phase 1)ではない**。DB間重複の削除は従来どおり `pipeline.py` が行う。
- 同一キーで本文が異なる場合は警告する(通常は文字コード違いのみ)。

【入力/出力】
  入力: <indir>/*.bib
  出力: 統合済み .bib (既定 <indir>/../<indir名>_merged.bib)

実行例:
  python -X utf8 scripts/merge_bib.py --indir raw/acm2 --out raw/acm_wave2_20260803.bib
  python -X utf8 scripts/merge_bib.py --indir raw/acm2 --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent

ENTRY_START = re.compile(r"^@\w+\{", re.M)
KEY_RE = re.compile(r"^@(\w+)\{([^,]+),")


def slice_num(p: Path) -> tuple:
    """ファイル名末尾の (n) で並べる。無ければ名前順。"""
    m = re.search(r"\((\d+)\)", p.name)
    return (0, int(m.group(1))) if m else (1, 0, p.name)


def split_entries(text: str) -> list[str]:
    idx = [m.start() for m in ENTRY_START.finditer(text)]
    return [text[s: idx[i + 1] if i + 1 < len(idx) else len(text)].rstrip() + "\n"
            for i, s in enumerate(idx)]


def main() -> None:
    ap = argparse.ArgumentParser(description="分割 .bib を引用キー単位で一意化して統合する")
    ap.add_argument("--indir", type=Path, required=True, help="*.bib を含むディレクトリ")
    ap.add_argument("--out", type=Path, default=None, help="出力 .bib (既定: <indir名>_merged.bib)")
    ap.add_argument("--dry-run", action="store_true", help="書き込まず集計だけ表示する")
    args = ap.parse_args()

    indir = args.indir
    if not indir.is_dir():
        sys.exit(f"[ERROR] ディレクトリがありません: {indir}")
    files = sorted(indir.glob("*.bib"), key=slice_num)
    if not files:
        sys.exit(f"[ERROR] {indir} に .bib がありません")

    out_path = args.out or indir.parent / f"{indir.name}_merged.bib"

    merged: dict[str, str] = {}
    first_seen: dict[str, str] = {}
    conflicts: list[str] = []
    total = 0

    print(f"[INFO] 入力 {len(files)} ファイル")
    for p in files:
        entries = split_entries(p.read_text(encoding="utf-8", errors="replace"))
        new = 0
        for e in entries:
            m = KEY_RE.match(e)
            if not m:
                continue
            key = m.group(2).strip()
            total += 1
            if key in merged:
                if merged[key] != e:
                    conflicts.append(f"{key} ({first_seen[key]} vs {p.name})")
                continue
            merged[key] = e
            first_seen[key] = p.name
            new += 1
        print(f"    {p.name:<16} {len(entries):>5}件  → 新規 {new:>5}")

    print(f"\n[INFO] 全エントリ {total:,} 件 / ユニーク {len(merged):,} 件"
          f" (重複 {total - len(merged):,} 件を除去)")
    if conflicts:
        print(f"[WARN] 同一キーで本文が異なるもの {len(conflicts)} 件"
              f"(先に現れた方を採用。通常は文字コード違い):")
        for c in conflicts[:10]:
            print(f"    {c}")
        if len(conflicts) > 10:
            print(f"    ... 他 {len(conflicts) - 10} 件")

    if args.dry_run:
        print("\n[DRY-RUN] ファイルは書き込んでいません。")
        return

    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(merged.values()))
    print(f"\n[INFO] 出力: {out_path}  ({len(merged):,} エントリ)")
    print("[NEXT] Zotero に専用コレクションで取り込み → CSV エクスポート → raw/ へ。")
    print("       その後 `python -X utf8 scripts/export_completeness_audit.py` で完全性を検証すること。")


if __name__ == "__main__":
    main()
