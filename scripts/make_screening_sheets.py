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

【体制(protocol_changelog.md Rev.17): liberal accelerated】
「**1人が Include にすれば通す。Exclude するには2人必要**」。

  stage 1  著者が全件を判定 + 校正セット(15%)は3名全員が判定
  stage 2  著者が Exclude / Unsure にしたものだけ第2評価者が確認
           (`make_screening_stage2.py` で生成)

Phase 3b のエラーは非対称で、誤 Exclude は回復不能(全文を読む機会が永久に失われる)だが、
誤 Include は Phase 4 の手間が増えるだけである。**除外の方向にだけ2人を要求する**ことで、
工数を抑えつつ感度を2人体制と同等に保つ。単独スクリーニングは関連文献の 13% を見落とす
(2人体制は 3%)という RCT の実測が根拠。

**校正セットが必須**である理由は下の `is_calibration` のコメントを参照
(除外プールだけでは κ が常に 0 になるため)。

【割当の決定論性】
校正セットの抽出も第2評価者の振り分けも、文献キー(DOI 優先・正規化タイトル代替)の
MD5 から決める。乱数を使わないので**誰がいつ実行しても同じ割当**になり、コーパスが
多少変わっても既存文献の割当は動かない(再実行時に判定済みの作業が無駄にならない)。

【トリアージ列について(重要)】
`kw_groups` は Rev.6 統合クエリの3概念群が Title+Abstract にいくつ成立するかで、
**読む順序を決めるためだけ**に使う。この値による自動除外はしない(rule.md Rev.2:
意味的判断は人手のみ)。シートは kw_groups の降順で並べてあるが、
**全件を判定する義務は変わらない**。

【出力】
  screening/assignment.csv         割当の正(record_id・calibration・第2評価者)
  screening/sheet_author.csv       著者の判定シート(全1,052件)
  screening/sheet_kataoka.csv      Kataoka の stage 1 シート(校正セットのみ)
  screening/sheet_watanabe.csv     WATANABE の stage 1 シート(校正セットのみ)

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

from pipeline import EXCLUSION_CATEGORIES, compile_exclusions, screen_keywords  # noqa: E402

# --- 評価者体制 ------------------------------------------------------------
REVIEWERS = {
    "author":   "著者",
    "kataoka":  "Yuta Kataoka",
    "watanabe": "Ryoichi WATANABE",
}
SECOND_REVIEWERS = ["kataoka", "watanabe"]   # 除外プールを分担する2名

# 旧 Rev.9 のペア分担(--design pair で使える。既定は liberal)
BLOCK_PAIRS = {
    0: ("author", "kataoka"),
    1: ("author", "watanabe"),
    2: ("kataoka", "watanabe"),
}

# --- liberal accelerated(Rev.17) -------------------------------------------
# 「1人が Include にすれば通す。Exclude するには2人必要」。
#
# 【なぜ】Phase 3b のエラーは非対称である。誤って Exclude すると全文を読む機会が
# 永久に失われる(回復不能)が、誤って Include しても Phase 4 の手間が増えるだけ。
# 単独スクリーニングは関連文献の 13% を見落とす(2人体制は 3%)という RCT の実測が
# あるため、**除外の方向にだけ2人を要求する**ことで、工数を抑えつつ感度を保つ。
# 本プロトコルが既に採っている「除外できると確信できないものは残す」「協議で解決
# しなければ Include に倒す」という再現率優先の思想とも一致する。
#
# 【★ 校正セットが必須である理由(実装上の要点)】
# 除外プールだけで Cohen's κ を計算すると、著者側の判定が定義上すべて Exclude で
# 分散がないため **Pe = Po となり κ が実際の一致率によらず常に 0** になる。
# したがって κ を報告するには、**3名全員が全判定を行う校正セット**が別に必要。
# ここでは判定対象の 15% を決定論的に抽出して校正セットとする。
# (副次的な効果として、本作業前の判断基準のすり合わせにもなる)
CALIBRATION_PCT = 15


def is_calibration(key: str, pct: int = CALIBRATION_PCT) -> bool:
    """校正セットに入るか。決定論的(乱数は使わない)でブロック割当とは独立にする。"""
    return int(hashlib.md5(("cal:" + key).encode("utf-8")).hexdigest(), 16) % 100 < pct


def second_reviewer_of(key: str) -> str:
    """除外プールの第2評価者。決定論的に2名へ振り分ける。"""
    h = int(hashlib.md5(("2nd:" + key).encode("utf-8")).hexdigest(), 16)
    return SECOND_REVIEWERS[h % len(SECOND_REVIEWERS)]

# --- トリアージ用の概念群(Rev.6 統合クエリ。除外には使わない) ---------------
KW_GROUPS = {
    "g1": re.compile(r"\b(virtual realit\w*|vr|hmds?|head[- ]mounted displays?"
                     r"|virtual environment\w*|immersive virtual)\b", re.I),
    "g2": re.compile(r"\b(avatars?|bod(?:y|ies|ily)|embodiment|embodied)\b", re.I),
    "g3": re.compile(r"\b(sizes?|scal\w*|heights?|distances?)\b", re.I),
}

SHEET_COLS = [
    "record_id", "block", "calibration", "source", "kw_groups", "has_abstract",
    "abstract_source",
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


def load_snowball(path: Path, exclusions) -> list[dict]:
    """引用探索の結果(PRISMA 右カラム)を判定シート用の共通スキーマに正規化する。

    【右カラムに適用する / しない基準(snowballing_protocol.md §3・§4.3)】
      - Phase 1.5 フィルタ層 … **適用しない**。目的が「DB間の検索scope差の吸収」であり、
        DB検索で取得していない文献には吸収すべき差が存在しない。かつ「クエリが
        取りこぼしたものを拾う」のが目的なのにクエリを再適用するのは自己矛盾。
      - Phase 2 Venueランク  … **適用しない**(§4.3 で確定済み)。実測では、適用すると
        257件中165件(64%)が消え、その83%は品質判断ではなく**照合失敗**
        (未照合88 / venue名なし49)だった。Science・Cognition・Presence・ICAT-EGVE 等の
        主要誌/回収対象の会場が含まれる。右カラムの venue 文字列は Crossref/S2 由来で
        非正規(短縮形が多い)であり、左カラム(Zotero 正規化済み)と照合の前提が違う。
      - Phase 3a キーワード除外 … **適用する**。これは PICOS 由来の適格性基準であり、
        「検索経路が違うだけで包含基準は緩めない」(§3)に従う。
      - Phase 3b 人手判定 … **適用する**。PRISMA 2020 の公式フロー図では右カラムに
        Title/Abstract 段が無く全文評価へ直行する想定だが、本レビューの右カラムは
        機械生成で人手フィルタを経ていないため、**規定より慎重に**この段を設ける。
    """
    if not path.exists():
        print(f"[WARN] {path.name} が無いため引用探索分は含めない")
        return []
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        raw_rows = [r for r in csv.DictReader(f) if r.get("in_db_already") == "N"]

    out, seen_local, no_title, kw_excluded = [], set(), 0, 0
    for r in raw_rows:
        title = (r.get("found_title") or "").strip()
        doi = norm_doi(r.get("found_doi", ""))
        k = doi if doi else "T:" + norm_title(title)
        if not title:
            no_title += 1          # §4.4: 手作業での同定対象。シートには載せない
            continue
        if k in seen_local:
            continue               # シード間の重複
        seen_local.add(k)
        abstract = (r.get("found_abstract") or "").strip()
        cats, _ = screen_keywords(f"{title} {abstract}", exclusions)
        if cats:
            kw_excluded += 1
            continue
        out.append({
            "Title": title,
            "Abstract Note": abstract,
            "DOI": r.get("found_doi", ""),
            "Publication Title": (r.get("found_venue") or "").strip(),
            "Publication Year": (r.get("found_year") or "").strip(),
            "Ranking_Source": "",   # 右カラムには venue フィルタを適用しない
            "__source__": "snowballing",
        })
    print(f"[INFO] 引用探索: 新規 {len(raw_rows)} 行 → ユニーク {len(seen_local):,} 件")
    print(f"       タイトル取得不能 {no_title} 件は除外(手作業で同定・§4.4)")
    print(f"       Phase 3a キーワード除外 {kw_excluded} 件")
    print(f"       → 判定対象 {len(out):,} 件")
    return out


def load_abstract_cache(path: Path) -> dict[str, str]:
    """`enrich_screening_abstracts.py` が作った要旨キャッシュ(DOI → 要旨)。

    **この要旨は人手判定の材料としてのみ使う。** Phase 1.5(フィルタ層)や Phase 3a
    (キーワード除外)を再適用してはならない。理由は enrich_screening_abstracts.py の
    ヘッダを参照(要約: 既に「判定不能なので人手に委ねる」と決めたレコードについて、
    検索が見ていない外部データで自動除外を発動させることになるため)。
    """
    if not path.exists():
        return {}
    out = {}
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        for r in csv.DictReader(f):
            a = (r.get("abstract") or "").strip()
            if a and r.get("doi"):
                out[r["doi"]] = a
    return out


def rank_label(row: dict) -> str:
    src = row.get("Ranking_Source", "") or ""
    if src.startswith("CORE"):
        return f"CORE {row.get('CORE_Rank', '')}".strip()
    if src.startswith("SJR"):
        return f"SJR {row.get('SJR_Quartile', '')}".strip()
    if row.get("__source__") == "snowballing":
        return "—(引用探索)"
    return src


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Phase 3b 判定シートの生成(評価者ごとに独立したファイル)")
    ap.add_argument("--input", type=Path, default=ROOT / "step3_kw_included.csv")
    ap.add_argument("--snowball", type=Path,
                    default=ROOT / "outputs" / "snowballing_log.csv",
                    help="引用探索の結果(PRISMA 右カラム)。--no-snowball で無効化")
    ap.add_argument("--no-snowball", action="store_true",
                    help="引用探索分を含めない(左カラムのみで生成する)")
    ap.add_argument("--abstract-cache", type=Path,
                    default=ROOT / "outputs" / "enriched_abstracts.csv",
                    help="DOI から補完した要旨のキャッシュ(人手判定の材料としてのみ使う)")
    ap.add_argument("--outdir", type=Path, default=ROOT / "screening")
    ap.add_argument("--dry-run", action="store_true", help="件数だけ表示して書き込まない")
    args = ap.parse_args()

    if not args.input.exists():
        sys.exit(f"[ERROR] 入力がありません: {args.input}")

    with args.input.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit(f"[ERROR] {args.input.name} が空です")

    print(f"[INFO] 入力: {args.input.name}  {len(rows):,} 件(左カラム=DB検索)")
    abs_cache = load_abstract_cache(args.abstract_cache)
    if abs_cache:
        print(f"[INFO] 要旨キャッシュ: {len(abs_cache):,} 件を読み込み"
              f"({args.abstract_cache.name})")
    if not args.no_snowball:
        rows = rows + load_snowball(args.snowball,
                                    compile_exclusions(EXCLUSION_CATEGORIES))

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
        cal = is_calibration(key)
        title = (row.get("Title") or "").strip()
        abstract = (row.get("Abstract Note") or "").strip()
        abs_src = "database" if abstract else "none"
        if not abstract:
            enriched = abs_cache.get(norm_doi(row.get("DOI", "")))
            if enriched:
                abstract, abs_src = enriched, "enriched"

        assignment.append({
            "record_id": rid,
            "block": blk + 1,
            "calibration": "Y" if cal else "N",
            # 校正セットは3名全員が判定する。それ以外は著者が判定し、
            # 著者が Exclude にしたものだけ第2評価者が確認する(stage 2 で配る)。
            "reviewer_a": "author",
            "reviewer_b": ("all" if cal else second_reviewer_of(key)),
            "key": key,
            "title": title,
            "doi": norm_doi(row.get("DOI", "")),
        })

        sheet_row = {
            "record_id": rid,
            "block": blk + 1,
            "calibration": "Y" if cal else "N",
            "source": "snowballing" if row.get("__source__") == "snowballing" else "database",
            "abstract_source": abs_src,
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
        # stage 1: 著者は全件。他2名は校正セットのみ。
        per_reviewer["author"].append(sheet_row)
        if cal:
            for r in SECOND_REVIEWERS:
                per_reviewer[r].append(dict(sheet_row))

    if dup:
        print(f"[WARN] 入力に重複キー {dup} 件。先出を採用した")

    # 読む順序のトリアージ: 概念群の多い順 → 年の新しい順
    for rid_list in per_reviewer.values():
        rid_list.sort(key=lambda r: (-r["kw_groups"], -int(r["year"] or 0)))

    # --- サマリ -------------------------------------------------------------
    n = len(assignment)
    n_cal = sum(1 for a in assignment if a["calibration"] == "Y")

    print(f"\n[INFO] 判定対象 {n:,} 件(ユニーク) — liberal accelerated 方式")
    print(f"  校正セット(3名全員が判定・κ の算出基盤): {n_cal:,} 件 ({n_cal / n * 100:.0f}%)")
    print(f"  著者のみが判定                        : {n - n_cal:,} 件")
    print("  ※ 著者が Exclude にしたものは stage 2 で第2評価者へ配る")
    print("     (Include は1人の判断で通す = liberal accelerated)")
    src_dist = {}
    for lst in per_reviewer.values():
        for r in lst:
            src_dist[r["source"]] = src_dist.get(r["source"], 0) + 1
    print(f"  取得経路別(のべ判定数): "
          f"DB検索 {src_dist.get('database', 0):,} / 引用探索 {src_dist.get('snowballing', 0):,}")
    print("  評価者別の担当件数:")
    for r, lst in per_reviewer.items():
        print(f"    {REVIEWERS[r]:18s}: {len(lst):5,d} 件")
    total = sum(len(v) for v in per_reviewer.values())
    print(f"  stage 1 の判定数: {total:,}")
    print(f"  ※ stage 2(著者の Exclude 分)は著者の記入完了後に "
          f"`make_screening_stage2.py` で生成する")

    # Abstract 欠落は Phase 3b の判定品質に直結するので必ず警告する
    no_abs_ids = {r["record_id"] for lst in per_reviewer.values()
                  for r in lst if r["has_abstract"] == "N"}
    total_no_abs = len(no_abs_ids)
    enriched_ids = {r["record_id"] for lst in per_reviewer.values()
                    for r in lst if r["abstract_source"] == "enriched"}
    if enriched_ids:
        print(f"\n[INFO] 要旨を DOI から補完したもの: {len(enriched_ids):,} 件"
              f"(`abstract_source=enriched` 列で識別できる)")
        print("       ★ この要旨は**人手判定の材料としてのみ**使う。"
              "Phase 1.5 / Phase 3a を再適用してはならない")
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
        w = csv.DictWriter(f, fieldnames=["record_id", "block", "calibration",
                                          "reviewer_a", "reviewer_b", "key", "title", "doi"])
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
