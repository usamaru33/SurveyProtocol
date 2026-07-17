#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
normalization_collision_audit.py — 正規化同名衝突の全数検出
================================================================================

【何を】
CORE / SJR の全エントリに pipeline.py と同一の正規化を適用してキー空間を再構築し、
**同一の正規化キーに2つ以上の異なる元エントリが対応する全ケース(=同名衝突)**を列挙する。
衝突のうち「採否(A*/A/Q1 か圏外か)が変わる」ものを別ファイルに抽出し、
venue_aliases.csv に「著者確認待ち」行として自動追記する。

【なぜ】
Presence 誌の誤照合(29件)・TAP 誌の誤照合(49件)は、ファジー照合ではなく
**正規化のストップワード除去による同名衝突(exact_norm 段階)**で発生しており、
類似度ベースの監査(venue_match_audit.py の fuzzy 抽出)では原理的に検出できない。
このクラスを網羅的に検出する専用監査が必要(protocol_changelog.md Rev.6 参照)。

【検出範囲の限界(重要)】
本監査は「ランキングリスト内・リスト間」の衝突を検出する。
**「データ側の短いVenue名 × リストエントリ」型の衝突**(例: データの 'Presence' が
正規化で CORE ワークショップと同一キーになるが、リスト内には衝突相手がいないケース)は、
リストエントリ同士では衝突しないため本監査では出ない。このクラスは
venue_match_audit.py の Task D 優先度付け(P2: 元文字列類似度が低い照合)で捕捉する。
※ TAP/SAP は SJR誌とCORE会議の**リスト間衝突**なので本監査で検出される。

【入力】
  - CORE.csv / scimagojr 2025.csv
  - step1_dedup.csv(現行データでの出現件数の算出用)
  - venue_aliases.csv(自動追記先)

【出力】
  - outputs/normalization_collisions.csv
      normalized_key | original_entries(pipe区切り) | ranks | key_kinds |
      affected_records_in_our_data | data_venue_examples | current_match_target |
      priority_flag(データに出現するものを HIGH)
  - outputs/collisions_rank_conflict.csv(採否が変わる衝突のみ)
  - venue_aliases.csv への自動追記(rank_conflict 全件、rank=MANUAL の文書化行。
    既に同じ衝突キーが記載済みの場合はスキップ = 冪等)
  - 標準出力: 件数サマリ

【方法(決定論的)】
  pipeline.normalize_venue / CSV の行順(後勝ち)を忠実に再現。乱数・AI 不使用。

実行: python -X utf8 scripts/normalization_collision_audit.py
"""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
sys.path.insert(0, str(ROOT))

from pipeline import (  # noqa: E402
    HIGH_RANKS,
    extract_parenthesized_acronym,
    normalize_venue,
)

ALIAS_PATH = ROOT / "venue_aliases.csv"


def adopted(source: str, rank: str) -> bool:
    return (source == "CORE" and rank in HIGH_RANKS) or \
           (source == "SJR" and rank == "Q1")


def build_keyspace():
    """pipeline.load_core / load_sjr と同一のキー生成を、衝突を潰さずに再現する。
    Returns: key -> list of dicts(source, kind, original, rank, order)"""
    keyspace: dict[str, list[dict]] = defaultdict(list)
    order = 0

    with (ROOT / "CORE.csv").open(encoding="utf-8-sig", newline="",
                                  errors="replace") as f:
        for row in csv.reader(f):
            if len(row) < 5:
                continue
            title, acronym, rank = row[1].strip(), row[2].strip(), row[4].strip()
            if not title:
                continue
            order += 1
            keyspace[normalize_venue(title)].append(
                {"source": "CORE", "kind": "norm_title", "original": title,
                 "rank": rank, "order": order})
            if acronym:
                keyspace[acronym.lower()].append(
                    {"source": "CORE", "kind": "acronym", "original": title,
                     "rank": rank, "order": order})

    with (ROOT / "scimagojr 2025.csv").open(encoding="utf-8-sig", newline="",
                                            errors="replace") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader, [])
        ti, qi = header.index("Title"), header.index("SJR Best Quartile")
        for row in reader:
            if len(row) <= max(ti, qi):
                continue
            title = row[ti].strip().strip('"')
            q = row[qi].strip().strip('"')
            if not title:
                continue
            order += 1
            keyspace[normalize_venue(title)].append(
                {"source": "SJR", "kind": "norm_title", "original": title,
                 "rank": q, "order": order})
            keyspace[title.lower()].append(
                {"source": "SJR", "kind": "lower_title", "original": title,
                 "rank": q, "order": order})
    return keyspace


def data_venue_index():
    """現行データ(step1_dedup.csv)の Venue が pipeline の照合でどのキーに解決するかを数える。
    Returns: key -> Counter(raw_venue -> record count)"""
    hits: dict[str, Counter] = defaultdict(Counter)
    venues: Counter[str] = Counter()
    with (ROOT / "step1_dedup.csv").open(encoding="utf-8-sig", newline="",
                                         errors="replace") as f:
        for row in csv.DictReader(f):
            venues[(row.get("Publication Title") or "").strip()] += 1
    for v, n in venues.items():
        if not v:
            continue
        keys = {normalize_venue(v), v.lower()}
        acr = extract_parenthesized_acronym(v)
        if acr:
            keys.add(acr.lower())
            keys.add(normalize_venue(acr))
        for k in keys:
            if k:
                hits[k][v] += n
    return hits


def current_winner(entries: list[dict]) -> dict:
    """pipeline での実効的な照合先: CORE が SJR より優先、同一リスト内は後勝ち(dict上書き)。"""
    core = [e for e in entries if e["source"] == "CORE"]
    pool = core if core else entries
    return max(pool, key=lambda e: e["order"])


def main() -> None:
    keyspace = build_keyspace()
    dv = data_venue_index()
    outdir = ROOT / "outputs"
    outdir.mkdir(exist_ok=True)

    rows_all, rows_conflict = [], []
    for key, entries in keyspace.items():
        distinct = {(e["source"], e["original"]) for e in entries}
        if len(distinct) < 2:
            continue
        uniq = []
        seen = set()
        for e in sorted(entries, key=lambda x: x["order"]):
            sig = (e["source"], e["original"])
            if sig in seen:
                continue
            seen.add(sig)
            uniq.append(e)
        winner = current_winner(entries)
        affected = dv.get(key, Counter())
        n_affected = sum(affected.values())
        adoptions = {adopted(e["source"], e["rank"]) for e in uniq}
        rec = {
            "normalized_key": key,
            "original_entries": " | ".join(
                f"[{e['source']}:{e['kind']}] {e['original']}" for e in uniq),
            "ranks": " | ".join(f"{e['source']} {e['rank']}" for e in uniq),
            "key_kinds": " | ".join(sorted({e["kind"] for e in uniq})),
            "affected_records_in_our_data": n_affected,
            "data_venue_examples": " | ".join(
                f"{v} (x{c})" for v, c in affected.most_common(3)),
            "current_match_target":
                f"[{winner['source']} {winner['rank']}] {winner['original']}",
            "priority_flag": "HIGH" if n_affected > 0 else "",
            "rank_conflict": "Y" if len(adoptions) > 1 else "",
        }
        rows_all.append(rec)
        if len(adoptions) > 1:
            rows_conflict.append(rec)

    rows_all.sort(key=lambda r: (-r["affected_records_in_our_data"],
                                 r["normalized_key"]))
    rows_conflict.sort(key=lambda r: (-r["affected_records_in_our_data"],
                                      r["normalized_key"]))

    fields = list(rows_all[0].keys()) if rows_all else []
    with (outdir / "normalization_collisions.csv").open(
            "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows_all)
    with (outdir / "collisions_rank_conflict.csv").open(
            "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows_conflict)

    n_high = sum(1 for r in rows_all if r["priority_flag"] == "HIGH")
    n_high_recs = sum(r["affected_records_in_our_data"] for r in rows_all)
    n_conf_high = sum(1 for r in rows_conflict if r["priority_flag"] == "HIGH")
    print("=" * 68)
    print("  正規化同名衝突 監査サマリ")
    print("=" * 68)
    print(f"  衝突キー総数                     : {len(rows_all):>6,}")
    print(f"    うち現行データに出現(HIGH)     : {n_high:>6,} キー / "
          f"{n_high_recs:,} レコード")
    print(f"  採否が変わる衝突(rank_conflict) : {len(rows_conflict):>6,}")
    print(f"    うち現行データに出現(HIGH)     : {n_conf_high:>6,}")
    print(f"  出力: outputs/normalization_collisions.csv / "
          f"collisions_rank_conflict.csv")

    # --- venue_aliases.csv へ rank_conflict 全件を自動追記(冪等) ---
    existing = ALIAS_PATH.read_text(encoding="utf-8-sig") if ALIAS_PATH.exists() \
        else "Raw venue string,Canonical name,CORE/SJR rank,Source of decision,Note\n"
    added = 0
    lines_to_add = []
    today = date.today().isoformat()
    for r in rows_conflict:
        key = r["normalized_key"]
        marker = f"衝突キー'{key}'"
        if marker in existing:
            continue  # 既に記載済み(冪等)
        affected = dv.get(key, Counter())
        raw = affected.most_common(1)[0][0] if affected else key
        note = (f"{marker}: {r['original_entries']} / ranks: {r['ranks']} / "
                f"データ{r['affected_records_in_our_data']}件。"
                "採否が変わる衝突のため要判断(normalization_collision_audit 自動検出)")
        vals = [raw, "(要著者判断)", "MANUAL",
                f"normalization_collision_audit 自動追記({today})・著者確認待ち", note]
        lines_to_add.append(",".join(
            '"' + v.replace('"', '""') + '"' if ("," in v or '"' in v) else v
            for v in vals))
        added += 1
    if lines_to_add:
        with ALIAS_PATH.open("a", encoding="utf-8-sig", newline="") as f:
            f.write("\n".join(lines_to_add) + "\n")
    print(f"  venue_aliases.csv へ自動追記     : {added} 行(MANUAL・著者確認待ち)"
          f"{' / 既存記載はスキップ' if added < len(rows_conflict) else ''}")


if __name__ == "__main__":
    main()
