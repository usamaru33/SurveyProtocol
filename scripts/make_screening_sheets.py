#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_screening_sheets.py — Phase 3b(Title/Abstract 二重スクリーニング)の判定シート生成
================================================================================

【何を】
`step3_kw_included.csv`(Phase 3a 通過の最終候補)から、評価者ごとの**独立した**
判定シートを生成する。あわせて、誰がどの文献を担当するかの割当表を出力する。

【なぜ独立したファイルに分けるのか】
二重スクリーニングの妥当性は**評価者が互いの判定を見ないこと**に依存する。
1枚のシートに両者の列を並べると、先に書いた側の判定が後の側に見えてしまい、
独立性が壊れて Cohen's κ が意味を失う。したがって:
  - 評価者ごとに別ファイル(`sheet_<id>.csv`)
  - 各シートには**自分の担当分しか入れない**
  - 他の評価者の判定列は存在しない
統合と κ 算出は `score_screening.py` が、全員の記入完了後に行う。

【体制(protocol_changelog.md Rev.9)】
評価者3名のペア分担。文献集合を3ブロックに分け、各ブロックを異なるペアに割り当てる。
各文献は必ず2名が独立に評価する。全員が全件を見る設計ではないため Fleiss' κ は用いず、
**ペアごとの Cohen's κ とその平均**を報告する。

  ブロック1 → 著者 × Kataoka
  ブロック2 → 著者 × WATANABE
  ブロック3 → Kataoka × WATANABE

【ブロック割当の決定論性】
割当は「文献キー(DOI 優先・正規化タイトル代替)の MD5 を 3 で割った余り」で決める。
乱数を使わないので**誰がいつ実行しても同じ割当**になり、コーパスが多少変わっても
既存文献の割当は動かない(再実行時に判定済みの作業が無駄にならない)。

【トリアージ列について(重要)】
`kw_groups` は Rev.6 統合クエリの3概念群が Title+Abstract にいくつ成立するかで、
**読む順序を決めるためだけ**に使う。この値による自動除外はしない(rule.md Rev.2:
意味的判断は人手のみ)。シートは kw_groups の降順で並べてあるが、
**全件を判定する義務は変わらない**。

【出力】
  screening/assignment.csv         割当の正(record_id・block・ペア・両評価者)
  screening/sheet_author.csv       著者の判定シート
  screening/sheet_kataoka.csv      Kataoka の判定シート
  screening/sheet_watanabe.csv     WATANABE の判定シート

実行:
  python -X utf8 scripts/make_screening_sheets.py
  python -X utf8 scripts/make_screening_sheets.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
sys.path.insert(0, str(ROOT))

csv.field_size_limit(10 ** 9)

# --- 評価者体制(Rev.9) -----------------------------------------------------
REVIEWERS = {
    "author":   "著者",
    "kataoka":  "Yuta Kataoka",
    "watanabe": "Ryoichi WATANABE",
}
# ブロック番号 → 担当ペア
BLOCK_PAIRS = {
    0: ("author", "kataoka"),
    1: ("author", "watanabe"),
    2: ("kataoka", "watanabe"),
}

# --- トリアージ用の概念群(Rev.6 統合クエリ。除外には使わない) ---------------
KW_GROUPS = {
    "g1": re.compile(r"\b(virtual realit\w*|vr|hmds?|head[- ]mounted displays?"
                     r"|virtual environment\w*|immersive virtual)\b", re.I),
    "g2": re.compile(r"\b(avatars?|bod(?:y|ies|ily)|embodiment|embodied)\b", re.I),
    "g3": re.compile(r"\b(sizes?|scal\w*|heights?|distances?)\b", re.I),
}

SHEET_COLS = [
    "record_id", "block", "kw_groups", "has_abstract",
    "title", "abstract", "venue", "year", "doi", "rank",
    "decision", "reason", "note",
]


def norm_doi(raw: str) -> str:
    d = (raw or "").strip().lower()
    d = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", d)
    return re.sub(r"^doi:\s*", "", d)


def norm_title(raw: str) -> str:
    t = re.sub(r"[^a-z0-9]+", " ", (raw or "").lower())
    return re.sub(r"\s+", " ", t).strip()


def record_key(row: dict) -> str:
    """文献の一意キー。known_item_test.py / merge_raw.py と同じ基準。"""
    d = norm_doi(row.get("DOI", ""))
    return d if d else "T:" + norm_title(row.get("Title", ""))


def record_id(key: str) -> str:
    """シート上の短い識別子。キーのハッシュ先頭10桁(衝突しない範囲で短く)。"""
    return "R" + hashlib.md5(key.encode("utf-8")).hexdigest()[:9]


def block_of(key: str) -> int:
    """決定論的なブロック割当(乱数は使わない)。"""
    return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % 3


def kw_group_count(title: str, abstract: str) -> int:
    text = f"{title or ''} {abstract or ''}"
    return sum(1 for rx in KW_GROUPS.values() if rx.search(text))


def rank_label(row: dict) -> str:
    src = row.get("Ranking_Source", "") or ""
    if src.startswith("CORE"):
        return f"CORE {row.get('CORE_Rank', '')}".strip()
    if src.startswith("SJR"):
        return f"SJR {row.get('SJR_Quartile', '')}".strip()
    return src


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Phase 3b 判定シートの生成(評価者ごとに独立したファイル)")
    ap.add_argument("--input", type=Path, default=ROOT / "step3_kw_included.csv")
    ap.add_argument("--outdir", type=Path, default=ROOT / "screening")
    ap.add_argument("--dry-run", action="store_true", help="件数だけ表示して書き込まない")
    args = ap.parse_args()

    if not args.input.exists():
        sys.exit(f"[ERROR] 入力がありません: {args.input}")

    with args.input.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit(f"[ERROR] {args.input.name} が空です")

    print(f"[INFO] 入力: {args.input.name}  {len(rows):,} 件")

    # --- 割当 ---------------------------------------------------------------
    assignment: list[dict] = []
    per_reviewer: dict[str, list[dict]] = {r: [] for r in REVIEWERS}
    seen: set[str] = set()
    dup = 0

    for row in rows:
        key = record_key(row)
        if key in seen:
            dup += 1
            continue
        seen.add(key)

        rid = record_id(key)
        blk = block_of(key)
        a, b = BLOCK_PAIRS[blk]
        title = (row.get("Title") or "").strip()
        abstract = (row.get("Abstract Note") or "").strip()

        assignment.append({
            "record_id": rid,
            "block": blk + 1,
            "reviewer_a": a,
            "reviewer_b": b,
            "key": key,
            "title": title,
            "doi": norm_doi(row.get("DOI", "")),
        })

        sheet_row = {
            "record_id": rid,
            "block": blk + 1,
            "kw_groups": kw_group_count(title, abstract),
            "has_abstract": "Y" if abstract else "N",
            "title": title,
            "abstract": abstract,
            "venue": (row.get("Publication Title") or "").strip(),
            "year": (row.get("Publication Year") or "").strip(),
            "doi": norm_doi(row.get("DOI", "")),
            "rank": rank_label(row),
            "decision": "",   # ← 評価者が記入(Include / Exclude / Unsure)
            "reason": "",     # ← Exclude 時は抵触した PICOS 基準を書く
            "note": "",
        }
        per_reviewer[a].append(sheet_row)
        per_reviewer[b].append(dict(sheet_row))

    if dup:
        print(f"[WARN] 入力に重複キー {dup} 件。先出を採用した")

    # 読む順序のトリアージ: 概念群の多い順 → 年の新しい順
    for rid_list in per_reviewer.values():
        rid_list.sort(key=lambda r: (-r["kw_groups"], -int(r["year"] or 0)))

    # --- サマリ -------------------------------------------------------------
    n = len(assignment)
    blocks = {i + 1: sum(1 for a in assignment if a["block"] == i + 1) for i in range(3)}

    print(f"\n[INFO] 判定対象 {n:,} 件(ユニーク)")
    print("  ブロック別:")
    for b, cnt in blocks.items():
        a1, a2 = BLOCK_PAIRS[b - 1]
        print(f"    ブロック{b}: {cnt:5,d} 件  ({REVIEWERS[a1]} × {REVIEWERS[a2]})")
    print("  評価者別の担当件数:")
    for r, lst in per_reviewer.items():
        print(f"    {REVIEWERS[r]:18s}: {len(lst):5,d} 件")
    print(f"  総判定数: {n * 2:,}(= {n:,} × 2名)")

    # Abstract 欠落は Phase 3b の判定品質に直結するので必ず警告する
    no_abs_ids = {r["record_id"] for lst in per_reviewer.values()
                  for r in lst if r["has_abstract"] == "N"}
    total_no_abs = len(no_abs_ids)
    print(f"\n[WARN] Abstract が無い文献 {total_no_abs:,} 件 "
          f"({total_no_abs / n * 100:.1f}%) — この文献は**タイトルのみ**での判定になる。")
    print("       `has_abstract=N` 列で識別できる。判定の信頼性が下がるため、")
    print("       `scripts/enrich_abstracts.py` による補完を先に検討すること。")

    if args.dry_run:
        print("\n[DRY-RUN] ファイルは書き込んでいない。")
        return

    args.outdir.mkdir(parents=True, exist_ok=True)

    # 割当表(正。評価者は編集しない)
    apath = args.outdir / "assignment.csv"
    with apath.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["record_id", "block", "reviewer_a",
                                          "reviewer_b", "key", "title", "doi"])
        w.writeheader()
        w.writerows(assignment)
    print(f"\n[INFO] 出力: {apath}  ({len(assignment):,} 行)")

    # 評価者ごとの独立シート
    for r, lst in per_reviewer.items():
        p = args.outdir / f"sheet_{r}.csv"
        if p.exists():
            print(f"[SKIP] {p.name} は既に存在する(記入済みを上書きしないため生成しない)")
            continue
        with p.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=SHEET_COLS, extrasaction="ignore")
            w.writeheader()
            w.writerows(lst)
        print(f"[INFO] 出力: {p}  ({len(lst):,} 行)  担当={REVIEWERS[r]}")

    print("\n[NEXT] 各評価者が自分の sheet_<id>.csv の decision 列に")
    print("       Include / Exclude / Unsure を記入する(reason は Exclude 時に必須)。")
    print("       **他の評価者のシートは開かないこと**(独立性が壊れる)。")
    print("       全員の記入後に `python -X utf8 scripts/score_screening.py` で")
    print("       Cohen's κ の算出と不一致リストの生成を行う。")


if __name__ == "__main__":
    main()
