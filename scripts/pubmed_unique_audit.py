#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pubmed_unique_audit.py — PubMed 固有レコードの抽出と主題適合率サンプルの整形
================================================================================

【Rev.8 追記(2026-07-22)】PubMed は不使用に確定(protocol_changelog.md Rev.8)。
本スクリプトと出力(outputs/pubmed_unique_175.csv)は**参考記録として保持**するが、
DB選定の意思決定には使わない(不使用の理由は「医学・治療目的でスコープ外」という
主題適合性であり、本スクリプトが測る corpus 固有寄与の大小とは独立)。
judge_relevance の記入タスクは優先度を格下げ済み。削除はしない(経緯として保存)。

【何を】
raw の PubMed コレクションにのみ存在し、他DB(ACM / IEEE / Scopus)には
DOI・正規化タイトルのどちらでも一致しないレコード(= PubMed 固有)を抽出する。
methodology_decision_Rev7.md §B で 175件と推定した層の実体を、著者が
主題適合/不適合を目視判定できる形に整形する。

【なぜ】
Rev.7 の判定: 4DB維持は確定だが、**PubMed の known-item 固有寄与は 0** であり、
PubMed 維持の正当化は「corpus 固有 175件」に依存している。この 175件が主題
(VR × 自己スケール/身体化)に適合しているほど PubMed の独立した価値が高い。
著者確認事項 #1(protocol_changelog.md Rev.7)の判定材料を用意する。

【入力】(すべてローカル、外部通信なし)
  raw/PubMed.csv                     判定対象
  raw/acm.csv, raw/ieee.csv,
  raw/Scopus.csv, raw/IEEE_2025-2026.csv   「他DB」の照合集合
  ※ 照合は pipeline / known_item_test と同一の norm_doi / norm_title。

【出力】
  outputs/pubmed_unique_175.csv
    - PubMed 固有の全レコード。列:
      in_sample_30, judge_relevance, Key, DOI, Year, Venue, Title, MeSH_terms,
      Abstract_excerpt
    - in_sample_30 = 'Y' の 30件は決定論的な無作為サンプル(random.seed(42))。
      judge_relevance 列は**空**で出力する。著者が 'Y'(主題適合) / 'N'(不適合)を記入する。

【著者の判定手順(LLM不使用)】
  1. in_sample_30 = 'Y' の 30 行について、Title / Abstract_excerpt / MeSH_terms を読み、
     judge_relevance に Y(VR×自己スケール/身体化の主題に適合)/ N(不適合)を記入。
  2. 適合率 p_hat = (Y の数) / 30 を算出。
  3. Wilson 95% 信頼区間(近似)で下限を確認する:
       p_hat ± 1.96 * sqrt(p_hat*(1-p_hat)/30)
     下限が実務的に十分高い(例 ≳ 0.3)なら「PubMed は独立した主題的寄与を持つ」と
     結論できる。低ければ PubMed の位置づけを「心理系 recall の保険 + PsycInfo 代替」に限定する。
  4. 結果と判断を PROGRESS_LOG.md / protocol_changelog.md に記録する。

実行: python -X utf8 scripts/pubmed_unique_audit.py
"""

from __future__ import annotations

import csv
import random
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
RAW = ROOT / "raw"
OUT = ROOT / "outputs" / "pubmed_unique_175.csv"

SAMPLE_N = 30
SEED = 42  # 再現性のため固定(誰が実行しても同じ 30 件になる)


def norm_doi(raw: str) -> str:
    d = (raw or "").strip().lower()
    d = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    return d


def norm_title(raw: str) -> str:
    t = (raw or "").lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        return list(csv.DictReader(f))


def keys_of(rows: list[dict]) -> set[str]:
    """レコード同一性キー: DOI があれば DOI、無ければ 'T:'+正規化タイトル。"""
    ks: set[str] = set()
    for r in rows:
        d = norm_doi(r.get("DOI", ""))
        if d:
            ks.add(d)
        else:
            t = norm_title(r.get("Title", ""))
            if t:
                ks.add("T:" + t)
    return ks


def rec_key(r: dict) -> str:
    d = norm_doi(r.get("DOI", ""))
    return d if d else "T:" + norm_title(r.get("Title", ""))


def main() -> None:
    pubmed = load(RAW / "PubMed.csv")
    others_files = ["acm.csv", "ieee.csv", "Scopus.csv", "IEEE_2025-2026.csv"]
    other_keys: set[str] = set()
    for fn in others_files:
        p = RAW / fn
        if p.exists():
            other_keys |= keys_of(load(p))

    unique = [r for r in pubmed if rec_key(r) not in other_keys]
    print(f"[INFO] PubMed 総 {len(pubmed)} 件 / 他DB照合集合 {len(other_keys)} キー")
    print(f"[INFO] PubMed 固有(他DBに DOI・正規化タイトルとも不一致): {len(unique)} 件")
    print("[INFO] ※ methodology_decision_Rev7.md §B の推定値(175)との差は "
          "IEEE 更新検索の追加照合分。実測値を採用のこと。")

    # 決定論的な 30 件無作為サンプル
    idx = list(range(len(unique)))
    random.Random(SEED).shuffle(idx)
    sample_idx = set(idx[:min(SAMPLE_N, len(unique))])

    OUT.parent.mkdir(exist_ok=True)
    fields = ["in_sample_30", "judge_relevance", "Key", "DOI", "Year",
              "Venue", "Title", "MeSH_terms", "Abstract_excerpt"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, r in enumerate(unique):
            abstract = (r.get("Abstract Note") or "").replace("\n", " ").strip()
            w.writerow({
                "in_sample_30": "Y" if i in sample_idx else "",
                "judge_relevance": "",  # 著者記入欄
                "Key": r.get("Key", ""),
                "DOI": norm_doi(r.get("DOI", "")),
                "Year": r.get("Publication Year", ""),
                "Venue": r.get("Publication Title", ""),
                "Title": (r.get("Title") or "").strip(),
                "MeSH_terms": (r.get("Manual Tags") or "").strip(),
                "Abstract_excerpt": abstract[:400],
            })
    print(f"[INFO] 出力: {OUT}(サンプル {len(sample_idx)} 件に judge_relevance 空欄を用意)")


if __name__ == "__main__":
    main()
