#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_completeness_audit.py — DB別エクスポートの「取りこぼし」検出
================================================================================

【何を】
`raw/` に置かれた DB別エクスポート CSV について、
(1) レコード数がエクスポート上限で**打ち切られていないか**、
(2) ファイル内・ファイル間の重複、
(3) 期待ヒット数(検索UIの表示件数)との一致、
(4) **gold set(既知文献)の当該DB分が含まれているか**、
(5) 出版年の分布(打ち切りが新しい年に偏っていないかの目視用)
を検査する。

【なぜ】
2026-08-02、ACM DL の再検索結果として置かれた 2ファイルが
**どちらも 1,000件ちょうどで打ち切られており**(実際のヒットは 6,012 / 8,328)、
さらに 2ファイルが同一レコードだったことが判明した。打ち切りは新しい年に偏っており、
gold set の ACM 3件のうち 2件(#7 2017年 / #13 2014年)が欠落していた。
この状態で Known-Item Test を回すと「recall が低い」という**誤った結論**が出る。

`search_replication.md` は以前から「全件取得の方法と取得件数の一致を確認」と
書いていたが、**確認する手段が無かった**ため見逃された。本スクリプトはその確認を機械化する。
とくに (4) の gold set 照合は、今回の問題を一発で捕まえられた検査である。

【入力】
  - raw/*.csv                    Zotero コレクション別エクスポート(ファイル名 = DB名/波)
  - self_scale_references.csv    gold set(SearchScope=in-scope を使用)

【出力】
  - outputs/export_completeness.csv   ファイル別の検査結果
  - 標準出力                          上記 + gold set 照合 + 警告

【方法(決定論的)】
  キーは DOI(正規化)優先・欠損時は正規化タイトル。`raw_db_audit.py` と同一基準。
  乱数・外部API・AI 判定は不使用。

実行例:
  python -X utf8 scripts/export_completeness_audit.py
  python -X utf8 scripts/export_completeness_audit.py --expect acm_wave2=14340
  python -X utf8 scripts/export_completeness_audit.py --files raw/acm_wave2_20260802.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
RAW_DIR = ROOT / "raw"
GOLD = ROOT / "self_scale_references.csv"

# エクスポートUIの典型的な上限。ちょうどこの件数だと打ち切りを疑う。
SUSPICIOUS_COUNTS = (100, 200, 250, 500, 1000, 2000, 5000, 10000)

# DOI 接頭辞 → DB名。gold set のどの文献がどのDBの担当かを機械判定する。
DOI_PREFIX_DB = {
    "10.1145": "ACM",
    "10.1109": "IEEE",
    "10.2312": "EG",       # Eurographics(EGVE 等) — ACM/IEEE いずれのDLにも無い
    "10.3389": "Frontiers",
    "10.1371": "PLOS",
    "10.1162": "MIT Press",
    "10.1073": "PNAS",
    "10.1007": "Springer",
}


def norm_doi(raw: str) -> str:
    d = (raw or "").strip().lower()
    d = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", d)
    return re.sub(r"^doi:\s*", "", d)


def norm_title(raw: str) -> str:
    t = re.sub(r"[^a-z0-9]+", " ", (raw or "").lower())
    return re.sub(r"\s+", " ", t).strip()


def key_of(doi: str, title: str) -> str:
    d = norm_doi(doi)
    return d if d else "T:" + norm_title(title)


def match_gold(item: dict, by_doi: dict[str, dict], by_title: dict[str, dict]) -> tuple[str, str]:
    """gold set の1件がコーパスに在るかを判定する。戻り値: (判定, 補足)。

    DOI 一致とタイトル一致を**別々に**評価するのが要点。
    「タイトルは一致するが DOI が違う」= 同名の別論文を誤って捕捉している可能性があり、
    Known-Item Test の偽陽性になる(2026-08-03 に #13 で実際に発生)。
    単一キーで突き合わせるとこの食い違いが見えなくなるため、必ず分けて判定する。
    """
    d = norm_doi(item["doi"])
    t = norm_title(item["title"])
    hit_doi = by_doi.get(d) if d else None
    hit_title = by_title.get(t) if t else None

    if hit_doi:
        return "HIT", ""
    if hit_title:
        found_doi = norm_doi(hit_title.get("DOI", ""))
        if d and found_doi and found_doi != d:
            return "SUSPECT", (f"タイトル一致だが DOI 不一致 (gold={d} / corpus={found_doi}, "
                               f"{hit_title.get('Publication Year','?')}年 "
                               f"{(hit_title.get('Publication Title') or '?')[:40]}) = 同名別論文の疑い")
        return "HIT", "タイトル一致(コーパス側に DOI 無し)"
    return "MISS", ""


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        return list(csv.DictReader(f))


def extract_doi(raw: str) -> str:
    """DOI_or_URL 列のような URL 混じりの文字列から DOI 本体を抜き出す。"""
    raw = (raw or "").strip()
    if raw.lower().startswith("10."):
        return raw
    m = re.search(r"10\.\d{4,9}/\S+", raw)
    return m.group(0) if m else ""


def load_gold() -> list[dict]:
    """gold set の in-scope 文献を読み、DOI 接頭辞から担当DBを判定して返す。"""
    if not GOLD.exists():
        return []
    items = []
    for row in load(GOLD):
        if (row.get("SearchScope") or "").strip() != "in-scope":
            continue
        doi = extract_doi(row.get("DOI_or_URL", ""))
        prefix = doi.split("/")[0] if doi else ""
        items.append({
            "id": (row.get("ID") or "?").strip(),
            "title": (row.get("Title") or "").strip(),
            "doi": doi,
            "db": DOI_PREFIX_DB.get(prefix, "other"),
        })
    return items


def db_label(path: Path) -> str:
    """ファイル名から担当DBを推定する(gold set 照合の対象を絞るため)。"""
    n = path.name.lower()
    if n.startswith("acm"):
        return "ACM"
    if n.startswith("ieee"):
        return "IEEE"
    if n.startswith("scopus"):
        return "Scopus"
    if n.startswith("pubmed"):
        return "PubMed"
    return "other"


def main() -> None:
    ap = argparse.ArgumentParser(
        description="raw/ のエクスポート完全性を検査する(ネットワーク不要・読み取り専用)")
    ap.add_argument("--files", type=Path, nargs="*", default=None,
                    help="検査対象CSV。省略時は raw/*.csv 全件")
    ap.add_argument("--expect", type=str, nargs="*", default=[],
                    help="期待ヒット数。'ファイル名の一部=件数' 形式 (例: acm_wave2=14340)")
    ap.add_argument("--outdir", type=Path, default=ROOT / "outputs")
    args = ap.parse_args()

    files = args.files if args.files else sorted(RAW_DIR.glob("*.csv"))
    if not files:
        sys.exit(f"[ERROR] 検査対象の CSV がありません: {RAW_DIR}")

    expect: dict[str, int] = {}
    for spec in args.expect:
        if "=" not in spec:
            sys.exit(f"[ERROR] --expect の書式が不正です: {spec} ('名前=件数' 形式)")
        name, _, num = spec.partition("=")
        try:
            expect[name.strip()] = int(num)
        except ValueError:
            sys.exit(f"[ERROR] --expect の件数が数値ではありません: {spec}")

    gold = load_gold()
    print(f"[INFO] 検査対象 {len(files)} ファイル / gold set in-scope {len(gold)} 件\n")

    rows_out: list[dict] = []
    keys_by_file: dict[str, set[str]] = {}
    warnings: list[str] = []
    corpus_by_doi: dict[str, dict] = {}
    corpus_by_title: dict[str, dict] = {}

    for path in files:
        if not path.exists():
            warnings.append(f"{path.name}: ファイルが存在しません")
            continue
        rows = load(path)
        n = len(rows)

        keys = [key_of(r.get("DOI", ""), r.get("Title", "")) for r in rows]
        uniq = set(keys)
        dup_in_file = n - len(uniq)
        keys_by_file[path.name] = uniq

        by_doi = {norm_doi(r.get("DOI", "")): r for r in rows if (r.get("DOI") or "").strip()}
        by_title = {norm_title(r.get("Title", "")): r for r in rows if (r.get("Title") or "").strip()}
        corpus_by_doi.update(by_doi)
        corpus_by_title.update(by_title)

        years = Counter((r.get("Publication Year") or "").strip() for r in rows)
        recent = sum(c for y, c in years.items() if y.isdigit() and int(y) >= 2021)
        recent_pct = (recent / n * 100) if n else 0.0

        has_abs = sum(1 for r in rows if (r.get("Abstract Note") or "").strip())
        has_doi = sum(1 for r in rows if (r.get("DOI") or "").strip())

        # --- 打ち切り判定 ---
        truncated = ""
        if n in SUSPICIOUS_COUNTS:
            truncated = f"件数が {n:,} ちょうど = エクスポート上限の疑い"
            warnings.append(f"{path.name}: {truncated}")

        # --- 期待値との突き合わせ ---
        exp_note = ""
        for name, num in expect.items():
            if name in path.name:
                if n == num:
                    exp_note = f"期待 {num:,} と一致"
                else:
                    exp_note = f"期待 {num:,} に対し {n:,} (差 {n - num:+,})"
                    warnings.append(f"{path.name}: {exp_note}")

        print(f"■ {path.name}")
        print(f"    レコード数     : {n:,}  (ユニーク {len(uniq):,} / ファイル内重複 {dup_in_file:,})")
        print(f"    DOI 充足       : {has_doi:,} ({has_doi / n * 100:.1f}%)" if n else "    DOI 充足       : -")
        print(f"    Abstract 充足  : {has_abs:,} ({has_abs / n * 100:.1f}%)" if n else "")
        print(f"    2021年以降     : {recent:,} ({recent_pct:.1f}%)")
        if truncated:
            print(f"    ⚠ {truncated}")
        if exp_note:
            print(f"    期待値         : {exp_note}")

        # --- gold set 照合(このファイルが担当するDBの分だけ。参考情報) ---
        lab = db_label(path)
        targets = [g for g in gold if g["db"] == lab]
        if targets:
            marks = []
            for g in targets:
                verdict, note = match_gold(g, by_doi, by_title)
                marks.append(verdict)
                print(f"        [{verdict:<7}] #{g['id']:>3} {g['doi']:<30} {g['title'][:44]}")
                if note:
                    print(f"                  └ {note}")
            print(f"    gold set({lab}) : HIT {marks.count('HIT')} / "
                  f"SUSPECT {marks.count('SUSPECT')} / MISS {marks.count('MISS')}"
                  f"  (全 {len(targets)} 件。単一DBでの MISS は他DBが捕捉していれば問題ない)")
        print()

        rows_out.append({
            "file": path.name,
            "db": lab,
            "records": n,
            "unique_keys": len(uniq),
            "dup_in_file": dup_in_file,
            "doi_filled": has_doi,
            "abstract_filled": has_abs,
            "since_2021_pct": f"{recent_pct:.1f}",
            "truncation_suspected": "Y" if truncated else "N",
            "expect_note": exp_note,
        })

    # --- ファイル間の重複 ---
    names = list(keys_by_file)
    if len(names) > 1:
        print("=== ファイル間の重複(ユニークキーの共通数) ===")
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                common = len(keys_by_file[a] & keys_by_file[b])
                if common:
                    print(f"    {a} ∩ {b} = {common:,}")
        print()

    # --- gold set の全体カバレッジ(これが本来の判定基準) ---
    if gold:
        print("=== gold set 全体カバレッジ(検査対象ファイルの和集合) ===")
        agg = Counter()
        for g in gold:
            verdict, note = match_gold(g, corpus_by_doi, corpus_by_title)
            agg[verdict] += 1
            if verdict != "HIT":
                print(f"    [{verdict:<7}] #{g['id']:>3} ({g['db']}) {g['doi']:<30} {g['title'][:44]}")
                if note:
                    print(f"              └ {note}")
            if verdict == "MISS":
                warnings.append(f"gold set #{g['id']} ({g['doi']}) がどのファイルにも無い")
            elif verdict == "SUSPECT":
                warnings.append(
                    f"gold set #{g['id']} はタイトル一致のみ(DOI不一致) = "
                    f"同名別論文を捕捉している疑い。要著者確認")
        total = len(gold)
        print(f"    → HIT {agg['HIT']}/{total} ({agg['HIT'] / total * 100:.1f}%) / "
              f"SUSPECT {agg['SUSPECT']} / MISS {agg['MISS']}")
        print("    ※ SUSPECT は recall を過大評価させる。Known-Item Test の値より優先して確認すること。\n")

    args.outdir.mkdir(parents=True, exist_ok=True)
    out_csv = args.outdir / "export_completeness.csv"
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()) if rows_out else ["file"])
        w.writeheader()
        w.writerows(rows_out)
    print(f"[INFO] 出力: {out_csv}")

    if warnings:
        print(f"\n⚠ 警告 {len(warnings)} 件:")
        for w_ in warnings:
            print(f"    - {w_}")
        print("\n打ち切りが疑われる場合は、検索UIの表示ヒット数と一致するまで")
        print("出版年でスライスして再エクスポートすること(docs/protocol/search_replication.md §1)。")
        sys.exit(1)

    print("\n[OK] 打ち切り・欠損の疑いは検出されませんでした。")


if __name__ == "__main__":
    main()
