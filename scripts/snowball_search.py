#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
snowball_search.py — Semantic Scholar API によるスノーボーリング(引用探索)の自動化
================================================================================

⚠️ 本スクリプトは **外部 API に通信する**。方針(既存の制約)により Claude は
   実行しない。**著者が手元環境で実行する**こと。ここではコードと手順のみ整備する。

【背景 / なぜ】
`docs/snowballing_protocol.md` は前方・後方引用探索の手順を定義しているが、
従来は Google Scholar / Semantic Scholar の Web UI を手作業で辿る前提だった。
本スクリプトは `docs-system/`(Semantic Scholar 連携の Next.js アプリ、
`lib/semantic-scholar.ts` の getCitations/getReferences)と同じ Semantic Scholar
Graph API を Python から叩き、シード論文の被引用・引用文献を機械的に取得する。

**PICOS採否・関連性の判断は自動化しない**(LLM不使用・決定論的の方針どおり)。
本スクリプトが行うのは「取得」と「機械的に分かる情報の付与」まで:
  - 既存コーパス(raw/*.csv・raw/*.ris・step3_kw_included.csv)に既出かどうか
  - CORE/SJR ランキング照合(参考情報。Phase 2 基準を通るかの目安)
著者はこの一覧を見て Title/採否/理由を判断し、`picos_decision` 列に記入する。

【シードの既定】
`docs/snowballing_protocol.md` §1.1 のとおり、既定シードは
`outputs/venue_dropped_known_items.csv`(step2脱落6件)を
`self_scale_references.csv`(# ↔ ID で結合)から DOI を引いて使う。
`--seeds-csv` で任意のCSV(Title/DOI列、エイリアス解決あり)に差し替え可能
(例: 2ホップ目に著者が選んだ候補を再投入する場合)。

【使い方】
  export SEMANTIC_SCHOLAR_API_KEY="..."   # 任意(無くても動くが rate limit が厳しい)
  # 既定シード(venue脱落6件)で前方・後方探索
  python -X utf8 scripts/snowball_search.py
  # 片方向のみ
  python -X utf8 scripts/snowball_search.py --directions backward
  # 著者が選んだ候補で2ホップ目
  python -X utf8 scripts/snowball_search.py --seeds-csv outputs/snowballing_hop2_seeds.csv

【出力】
  outputs/snowballing_log.csv  — 累積ログ(実行のたびに追記、既存行は保持)。
  列は docs/snowballing_protocol.md §4 の推奨列に、venue_rank_note の自動付与を加えたもの:
  seed_id, seed_title, direction, found_title, found_doi, found_year, found_venue,
  in_db_already, venue_rank_note, picos_decision(空欄・著者記入), reason(空欄・著者記入)

【注意】
- Semantic Scholar API はDOIが無い論文も paperId で管理される。本スクリプトは
  DOI があれば `paper/DOI:{doi}` で直接引き、無ければタイトル検索でフォールバックする
  (タイトル検索はあいまい一致になりうるため、結果は目視確認のこと)。
- rate limit: API キー無しは共有プールで厳しく制限される。キーがあれば緩和される
  (取得方法は `enrich_abstracts.py` と同じ、developer登録は不要でメール登録のみで発行される)。
- 既存コーパスとの重複判定は DOI 優先・無ければ正規化タイトルで行う(`known_item_test.py` と同一基準)。
  raw/*.ris(wave2の未取込データ)も簡易パースして重複判定に含める。
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
sys.path.insert(0, str(ROOT))

from api_search_common import load_dotenv, polite_get  # noqa: E402
from pipeline import load_core, load_sjr, normalize_venue  # noqa: E402

load_dotenv()

BASE_URL = "https://api.semanticscholar.org/graph/v1"
PAPER_FIELDS = "title,abstract,year,venue,externalIds"
REF_CIT_FIELDS = f"title,year,venue,externalIds"
MAX_HOPS_WARN = 2  # snowballing_protocol.md §2.3: 2ホップまで(超えたら警告のみ、強制はしない)


# ---------------------------------------------------------------------------
# 正規化(既存スクリプトと同一基準)
# ---------------------------------------------------------------------------

def norm_doi(raw: str) -> str:
    d = (raw or "").strip().lower()
    d = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    return d


def norm_title(raw: str) -> str:
    t = (raw or "").lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def extract_doi_from_field(raw: str) -> str:
    """DOI_or_URL 列のような、URL 混じりの文字列から DOI 本体を抜き出す。"""
    raw = (raw or "").strip()
    if not raw:
        return ""
    if raw.lower().startswith("10."):
        return raw
    m = re.search(r"10\.\d{4,9}/\S+", raw)
    return m.group(0) if m else ""


# ---------------------------------------------------------------------------
# 既存コーパスの読み込み(重複判定用)
# ---------------------------------------------------------------------------

def load_existing_keys() -> set[str]:
    """raw/*.csv・raw/*.ris・step3_kw_included.csv から DOI/正規化タイトルのキー集合を作る。"""
    keys: set[str] = set()

    for csv_path in (ROOT / "raw").glob("*.csv"):
        with csv_path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
            for row in csv.DictReader(f):
                d = norm_doi(row.get("DOI", ""))
                t = norm_title(row.get("Title", ""))
                if d:
                    keys.add(d)
                elif t:
                    keys.add("T:" + t)

    for ris_path in (ROOT / "raw").glob("*.ris"):
        keys |= _keys_from_ris(ris_path)

    step3 = ROOT / "step3_kw_included.csv"
    if step3.exists():
        with step3.open(encoding="utf-8-sig", newline="", errors="replace") as f:
            for row in csv.DictReader(f):
                d = norm_doi(row.get("DOI", ""))
                t = norm_title(row.get("Title", ""))
                if d:
                    keys.add(d)
                elif t:
                    keys.add("T:" + t)

    return keys


def _keys_from_ris(path: Path) -> set[str]:
    """RIS ファイルから DOI(DO)/タイトル(TI)を簡易パースしてキー化する(重複判定用のみ)。"""
    keys: set[str] = set()
    cur_doi, cur_title = "", ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("DO  - "):
            cur_doi = norm_doi(line[6:].strip())
        elif line.startswith("TI  - "):
            cur_title = norm_title(line[6:].strip())
        elif line.startswith("ER"):
            if cur_doi:
                keys.add(cur_doi)
            elif cur_title:
                keys.add("T:" + cur_title)
            cur_doi, cur_title = "", ""
    return keys


def key_of(doi: str, title: str) -> str:
    d = norm_doi(doi)
    if d:
        return d
    return "T:" + norm_title(title)


# ---------------------------------------------------------------------------
# シード読み込み
# ---------------------------------------------------------------------------

SEED_COL_ALIASES = {
    "id": ["#", "ID", "seed_id"],
    "title": ["Title", "title"],
    "doi": ["DOI", "DOI_or_URL", "doi"],
}


def _resolve(row: dict, aliases: list[str]) -> str:
    for a in aliases:
        if a in row and (row.get(a) or "").strip():
            return row[a].strip()
    return ""


def load_default_seeds() -> list[dict]:
    """venue_dropped_known_items.csv(#)を self_scale_references.csv(ID)と結合し、
    Title + DOI を持つシードのリストを作る。"""
    dropped_path = ROOT / "outputs" / "venue_dropped_known_items.csv"
    refs_path = ROOT / "self_scale_references.csv"
    if not dropped_path.exists() or not refs_path.exists():
        sys.exit(f"[ERROR] 既定シード読み込みに必要なファイルが見つかりません: "
                  f"{dropped_path.name} / {refs_path.name}")

    with refs_path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        refs_by_id = {row["ID"].strip(): row for row in csv.DictReader(f) if row.get("ID")}

    seeds = []
    with dropped_path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        for row in csv.DictReader(f):
            seed_id = (row.get("#") or "").strip()
            ref_row = refs_by_id.get(seed_id)
            if not ref_row:
                print(f"[WARN] seed #{seed_id} が self_scale_references.csv に見つかりません。スキップ")
                continue
            doi = extract_doi_from_field(ref_row.get("DOI_or_URL", ""))
            seeds.append({"id": seed_id, "title": ref_row.get("Title", "").strip(), "doi": doi})
    return seeds


def load_seeds_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        rows = list(csv.DictReader(f))
    seeds = []
    for i, row in enumerate(rows, start=1):
        title = _resolve(row, SEED_COL_ALIASES["title"])
        doi = extract_doi_from_field(_resolve(row, SEED_COL_ALIASES["doi"]))
        seed_id = _resolve(row, SEED_COL_ALIASES["id"]) or str(i)
        if title or doi:
            seeds.append({"id": seed_id, "title": title, "doi": doi})
    return seeds


# ---------------------------------------------------------------------------
# Semantic Scholar API
# ---------------------------------------------------------------------------

def _headers() -> dict:
    key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY") or os.environ.get("S2_API_KEY")
    return {"x-api-key": key} if key else {}


def resolve_paper_id(title: str, doi: str) -> tuple[str, dict] | tuple[None, None]:
    """DOI があれば直接引き、無ければタイトル検索でフォールバックする。戻り値: (paperId, paper dict)。"""
    if doi:
        resp = polite_get(f"{BASE_URL}/paper/DOI:{doi}", params={"fields": PAPER_FIELDS},
                           headers=_headers())
        if resp is not None and resp.status_code == 200:
            data = resp.json()
            return data.get("paperId"), data

    if title:
        resp = polite_get(f"{BASE_URL}/paper/search",
                           params={"query": title, "limit": 1, "fields": PAPER_FIELDS},
                           headers=_headers())
        if resp is not None and resp.status_code == 200:
            hits = resp.json().get("data") or []
            if hits:
                return hits[0].get("paperId"), hits[0]

    return None, None


def fetch_references(paper_id: str, limit: int = 200) -> list[dict]:
    resp = polite_get(f"{BASE_URL}/paper/{paper_id}/references",
                       params={"fields": REF_CIT_FIELDS, "limit": limit}, headers=_headers())
    if resp is None or resp.status_code != 200:
        return []
    return [e.get("citedPaper", {}) for e in (resp.json().get("data") or [])]


def fetch_citations(paper_id: str, limit: int = 200) -> list[dict]:
    resp = polite_get(f"{BASE_URL}/paper/{paper_id}/citations",
                       params={"fields": REF_CIT_FIELDS, "limit": limit}, headers=_headers())
    if resp is None or resp.status_code != 200:
        return []
    return [e.get("citingPaper", {}) for e in (resp.json().get("data") or [])]


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Semantic Scholar API によるスノーボーリング(著者実行用)")
    ap.add_argument("--seeds-csv", type=Path, default=None,
                    help="シードCSV(Title/DOI列)。省略時は venue_dropped_known_items.csv を既定使用")
    ap.add_argument("--directions", type=str, default="backward,forward",
                    help="backward(参考文献) / forward(被引用) / 両方はカンマ区切り(既定)")
    ap.add_argument("--limit-per-seed", type=int, default=200)
    args = ap.parse_args()

    directions = [d.strip() for d in args.directions.split(",") if d.strip()]
    for d in directions:
        if d not in ("backward", "forward"):
            sys.exit(f"[ERROR] 不明な direction: {d}(backward/forward のみ)")

    seeds = load_seeds_csv(args.seeds_csv) if args.seeds_csv else load_default_seeds()
    if not seeds:
        sys.exit("[ERROR] シードが0件です。")
    print(f"[INFO] シード {len(seeds)} 件({'既定(venue脱落6件)' if not args.seeds_csv else args.seeds_csv.name})")

    print("[INFO] 既存コーパス(raw/*.csv, raw/*.ris, step3_kw_included.csv)のキーを読み込み中...")
    existing_keys = load_existing_keys()
    print(f"[INFO] 既存キー {len(existing_keys)} 件")

    core = load_core(ROOT / "CORE.csv")
    sjr = load_sjr(ROOT / "scimagojr 2025.csv")

    rows: list[dict] = []
    for seed in seeds:
        print(f"[INFO] シード #{seed['id']}: {seed['title'][:60]}")
        paper_id, _ = resolve_paper_id(seed["title"], seed["doi"])
        if not paper_id:
            print(f"    [WARN] Semantic Scholar で解決できず(DOI/タイトルとも不一致)。スキップ")
            continue

        for direction in directions:
            found = fetch_references(paper_id, args.limit_per_seed) if direction == "backward" \
                else fetch_citations(paper_id, args.limit_per_seed)
            print(f"    {direction}: {len(found)} 件")

            for f in found:
                f_title = f.get("title") or ""
                f_doi = ((f.get("externalIds") or {}).get("DOI")) or ""
                if not f_title and not f_doi:
                    continue
                k = key_of(f_doi, f_title)
                in_db = "Y" if k in existing_keys else "N"

                venue = f.get("venue") or ""
                note = ""
                if venue:
                    norm = normalize_venue(venue)
                    if norm in core:
                        note = f"CORE {core[norm]['rank']}"
                    elif norm in sjr:
                        note = f"SJR {sjr[norm]['quartile']}"
                    else:
                        note = "未照合"

                rows.append({
                    "seed_id": seed["id"],
                    "seed_title": seed["title"],
                    "direction": direction,
                    "found_title": f_title,
                    "found_doi": norm_doi(f_doi),
                    "found_year": f.get("year") or "",
                    "found_venue": venue,
                    "in_db_already": in_db,
                    "venue_rank_note": note,
                    "picos_decision": "",  # 著者記入
                    "reason": "",          # 著者記入
                })

    out_path = ROOT / "outputs" / "snowballing_log.csv"
    is_new = not out_path.exists()
    fieldnames = ["seed_id", "seed_title", "direction", "found_title", "found_doi",
                  "found_year", "found_venue", "in_db_already", "venue_rank_note",
                  "picos_decision", "reason"]
    with out_path.open("a", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if is_new:
            w.writeheader()
        w.writerows(rows)

    new_candidates = sum(1 for r in rows if r["in_db_already"] == "N")
    print(f"\n[INFO] 追記 {len(rows)} 件(うち既存コーパスに無い新規候補 {new_candidates} 件)")
    print(f"[INFO] 出力: {out_path}")
    print("[NEXT] picos_decision 列に include/exclude、reason 列に理由を著者が記入すること。"
          "in_db_already=Y の行は 'other methods' に二重計上しないこと"
          "(docs/snowballing_protocol.md §4)。")


if __name__ == "__main__":
    main()
