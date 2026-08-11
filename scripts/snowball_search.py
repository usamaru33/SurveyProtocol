#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
snowball_search.py — Semantic Scholar API によるスノーボーリング(引用探索)の自動化
================================================================================

⚠️ 本スクリプトは **外部 API に通信する**(Semantic Scholar / Crossref)。
   既定では著者が手元環境で実行する。2026-08-06 に著者の明示的な指示により
   初回実行を行った(実行記録は `docs/PROGRESS_LOG.md`)。

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
  in_db_already, venue_rank_note, ref_source, picos_decision(空欄・著者記入), reason(空欄・著者記入)

【注意】
- Semantic Scholar API はDOIが無い論文も paperId で管理される。本スクリプトは
  DOI があれば `paper/DOI:{doi}` で直接引き、無ければタイトル検索でフォールバックする
  (タイトル検索はあいまい一致になりうるため、結果は目視確認のこと)。
- rate limit: API キー無しは共有プールで厳しく制限される。キーがあれば緩和される
  (取得方法は `enrich_abstracts.py` と同じ、developer登録は不要でメール登録のみで発行される)。
- 既存コーパスとの重複判定は DOI 優先・無ければ正規化タイトルで行う(`known_item_test.py` と同一基準)。
  raw/*.ris(wave2の未取込データ)も簡易パースして重複判定に含める。

【後方探索の制約(2026-08-06 実測)】
- **S2 は出版社が参考文献を非開示にしている論文がある**("elided by the publisher")。
  シード6件中 **4件**(ACM 3件・MIT Press 1件)がこれに該当し、`data: None` が返って
  後方探索が丸ごと空になっていた。**Crossref の reference リストにフォールバック**して回避する。
- Crossref にも無い場合(例: Eurographics の 10.2312 系は Crossref に未登録)は
  `ref_source=取得不可` として警告する。その方向は手作業での補完が必要。

【前方探索のページング(2026-08-06 修正)】
- S2 は1リクエスト最大1,000件・`offset+limit ≤ 10,000` の制約がある。
  旧実装は `limit=200` 固定でページングしておらず、**被引用の多い論文が黙って切り捨てられていた**
  (実例: Kilteni et al. 2012 は被引用1,497件だが200件しか取れていなかった)。
  現在は offset ページングで取り切り、API 上限に達した場合は `ref_source` に明示する。
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
CROSSREF_URL = "https://api.crossref.org/works"
PAPER_FIELDS = "title,abstract,year,venue,externalIds"
# 発見された文献にも **abstract を必ず含める**(2026-08-10 追加)。
# 理由が2つある:
#  (1) Phase 3b は Title/Abstract を人が読む手続きなので、要旨が無いログは
#      そのままではスクリーニングに使えず、著者が1件ずつ引きに行くことになる。
#  (2) 概念群(G1/G2/G3)の判定はタイトルだけでは成立しない。実測では
#      新規1,433件のうちタイトルで3群が揃うのは **0件**、IEEE 第2波で
#      実際に検索がヒットした文献でもタイトルのみ成立は 5% にすぎず、
#      91% が Title+Abstract で初めて成立する。
REF_CIT_FIELDS = f"title,abstract,year,venue,externalIds"
MAX_HOPS_WARN = 2  # snowballing_protocol.md §2.3: 2ホップまで(超えたら警告のみ、強制はしない)

# ---------------------------------------------------------------------------
# 概念群(Rev.6 統合クエリの G1/G2/G3)による**読む順序のトリアージ**
#
# 用途は「順序付け」であって「除外」ではない。citation searching の存在意義は
# 検索式が取りこぼした文献の回収なので、同じ検索式で機械的に切ると目的と矛盾する
# (venue フィルタを右カラムに適用しないのと同じ理屈。snowballing_protocol.md §4.3)。
# 除外に使う場合は**明示的な逸脱として PRISMA-S に記載**すること。
#
# 判定は Title + Abstract に対して行う(タイトルのみでは成立しない。上の
# REF_CIT_FIELDS のコメント参照)。決定論的・LLM 不使用。
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 用語定義シード — 前方探索を行わない(Rev.10、2026-08-10 実測にもとづく)
#
# #3 Kilteni et al. 2012 は「sense of embodiment(SoO/SoA/self-location)」の定義典拠であり、
# 被引用1,500件超。その被引用は「自己スケール文献」ではなく「身体化に言及する研究すべて」で、
# 新規候補1,188件のうち G3語(size/scale/height/distance)を含むのは11件、
# うち実際に主題適合なのは2件程度でしかなかった(残りは embodiment *scale*=質問紙尺度、
# large-*scale*=システム規模、aesthetic *distance*=比喩 等の誤爆)。
# 一方、**後方探索(参考文献65件)は高価値**で、Botvinick&Cohen 1998 / Lenggenhager 2007 /
# Slater 2010 / Petkova&Ehrsson 2008 の心理接合点の古典すべてに到達している
# (snowballing_protocol.md §1.3 が「到達目標」としていたもの)。
# したがって #3 は **後方のみ**とする。
# ---------------------------------------------------------------------------
DEFINITIONAL_SEEDS = ("3",)

KW_GROUPS = {
    "g1": re.compile(r"\b(virtual realit\w*|vr|hmds?|head[- ]mounted displays?"
                     r"|virtual environment\w*|immersive virtual)\b", re.I),
    "g2": re.compile(r"\b(avatars?|bod(?:y|ies|ily)|embodiment|embodied)\b", re.I),
    "g3": re.compile(r"\b(sizes?|scal\w*|heights?|distances?)\b", re.I),
}


def kw_flags(title: str, abstract: str) -> dict:
    """Title+Abstract に対する概念群の命中フラグと成立群数を返す。"""
    text = f"{title or ''} {abstract or ''}"
    hits = {g: ("Y" if rx.search(text) else "N") for g, rx in KW_GROUPS.items()}
    return {**{f"kw_{g}": v for g, v in hits.items()},
            "kw_groups": sum(1 for v in hits.values() if v == "Y")}


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


def _paged(endpoint: str, paper_id: str, item_key: str, limit_total: int) -> tuple[list[dict], bool]:
    """citations / references を offset ページングで取り切る。戻り値: (レコード, 打ち切られたか)。

    Semantic Scholar は1回のリクエストで最大1,000件、かつ offset+limit ≤ 10,000 の制約がある。
    ページングしないと被引用の多い論文が黙って切り捨てられる(実例: Kilteni et al. 2012 は
    被引用1,497件だが、旧実装の limit=200 では 200件しか取れていなかった)。
    """
    out: list[dict] = []
    offset = 0
    hard_cap = 10000
    while True:
        want = 1000 if limit_total <= 0 else min(1000, limit_total - len(out))
        if want <= 0:
            return out, True
        if offset + want > hard_cap:
            want = hard_cap - offset
            if want <= 0:
                return out, True
        resp = polite_get(f"{BASE_URL}/paper/{paper_id}/{endpoint}",
                          params={"fields": REF_CIT_FIELDS, "limit": want, "offset": offset},
                          headers=_headers())
        if resp is None or resp.status_code != 200:
            return out, False
        data = resp.json().get("data")
        if data is None:          # publisher による非開示(references で発生する)
            return out, False
        out.extend(e.get(item_key, {}) for e in data)
        if len(data) < want:
            return out, False
        offset += want


def _crossref_references(doi: str) -> list[dict]:
    """Crossref の reference リストを S2 と同じ形に整形して返す(後方探索の代替経路)。

    ACM/MIT Press 等は S2 に参考文献を開示していない("elided by the publisher")ため、
    後方探索が丸ごと空になる。Crossref には出版社が登録した参考文献が入っていることが多く、
    そちらを代替として使う。
    """
    resp = polite_get(CROSSREF_URL + "/" + doi, params={"mailto": os.environ.get("ENRICH_MAILTO", "")})
    if resp is None or resp.status_code != 200:
        return []
    out = []
    for ref in (resp.json().get("message", {}).get("reference") or []):
        title = (ref.get("article-title") or ref.get("volume-title")
                 or (ref.get("unstructured") or "")[:200])
        rdoi = ref.get("DOI") or ""
        if not title and not rdoi:
            continue
        out.append({
            "title": title,
            "year": ref.get("year") or "",
            "venue": ref.get("journal-title") or "",
            "externalIds": {"DOI": rdoi} if rdoi else {},
        })
    return out


def fetch_references(paper_id: str, doi: str, limit: int = 0) -> tuple[list[dict], str]:
    """後方探索。S2 が publisher 非開示なら Crossref にフォールバックする。"""
    recs, _ = _paged("references", paper_id, "citedPaper", limit)
    if recs:
        return recs, "S2"
    if doi:
        cr = _crossref_references(doi)
        if cr:
            return cr, "Crossref"
    return [], "取得不可"


def resolve_missing_metadata(records: list[dict]) -> int:
    """タイトル or 要旨を欠くレコードを、DOI から S2 で解決して埋める。

    【なぜ】Crossref の reference リストは DOI しか持たない項目が多く、要旨は一切返さない。
    2026-08-10 の実測では後方探索 173件のうち **93件(54%)がタイトル欠落**で、
    そのままでは Title/Abstract を読む Phase 3b にかけられなかった
    (前方探索は S2 由来なので欠落0件)。後方探索は #3 の参考文献から
    Botvinick&Cohen 1998 / Lenggenhager 2007 等の心理接合点の古典に到達できる
    **高価値な経路**であり、読めない状態で放置してはいけない。

    DOI が無いレコードは解決できない(タイトル照合は誤同定の危険があるため行わない)。
    戻り値: 解決できた件数。
    """
    targets = [r for r in records
               if ((r.get("externalIds") or {}).get("DOI"))
               and (not (r.get("title") or "").strip() or not (r.get("abstract") or "").strip())]
    if not targets:
        return 0
    print(f"        [INFO] タイトル/要旨の欠落 {len(targets)} 件を DOI から解決中...")
    filled = 0
    for r in targets:
        doi = (r.get("externalIds") or {}).get("DOI")
        resp = polite_get(f"{BASE_URL}/paper/DOI:{doi}",
                          params={"fields": PAPER_FIELDS}, headers=_headers())
        if resp is None or resp.status_code != 200:
            continue
        d = resp.json()
        for field in ("title", "abstract", "year", "venue"):
            if not (r.get(field) or "") and d.get(field):
                r[field] = d[field]
        if (r.get("title") or "").strip():
            filled += 1
    print(f"        [INFO] うち {filled} 件でタイトルを取得")
    return filled


def fetch_citations(paper_id: str, limit: int = 0) -> tuple[list[dict], str]:
    """前方探索。ページングで取り切る。"""
    recs, capped = _paged("citations", paper_id, "citingPaper", limit)
    return recs, ("S2(上限で打ち切り)" if capped else "S2")


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Semantic Scholar API によるスノーボーリング(著者実行用)")
    ap.add_argument("--seeds-csv", type=Path, default=None,
                    help="シードCSV(Title/DOI列)。省略時は venue_dropped_known_items.csv を既定使用")
    ap.add_argument("--directions", type=str, default="backward,forward",
                    help="backward(参考文献) / forward(被引用) / 両方はカンマ区切り(既定)")
    ap.add_argument("--limit-per-seed", type=int, default=0,
                    help="1シードあたりの取得上限(0=無制限。API側の offset 上限10,000まで)")
    ap.add_argument("--no-forward-seeds", type=str, default=",".join(DEFINITIONAL_SEEDS),
                    help=(f"前方探索を行わないシードID(カンマ区切り)。既定 '{','.join(DEFINITIONAL_SEEDS)}'"
                          f" = 用語定義シード(Rev.10)。空文字を渡すと全シードで前方探索する"))
    args = ap.parse_args()

    directions = [d.strip() for d in args.directions.split(",") if d.strip()]
    for d in directions:
        if d not in ("backward", "forward"):
            sys.exit(f"[ERROR] 不明な direction: {d}(backward/forward のみ)")

    no_forward = {s.strip() for s in args.no_forward_seeds.split(",") if s.strip()}
    if no_forward and "forward" in directions:
        print(f"[INFO] 前方探索を行わないシード: {sorted(no_forward)}"
              f"(用語定義シード。理由は snowballing_protocol.md §1.2)")

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
            if direction == "forward" and str(seed["id"]) in no_forward:
                print(f"    forward: スキップ(用語定義シードのため。"
                      f"snowballing_protocol.md §1.2 / changelog Rev.10)")
                continue

            if direction == "backward":
                found, src = fetch_references(paper_id, seed["doi"], args.limit_per_seed)
                # 後方探索は Crossref 経由だとタイトル・要旨が欠けるため必ず補完する
                resolve_missing_metadata(found)
            else:
                found, src = fetch_citations(paper_id, args.limit_per_seed)
            print(f"    {direction}: {len(found)} 件  (出典: {src})")
            if src == "取得不可":
                print("        [WARN] S2 は publisher 非開示、Crossref にも参考文献なし。"
                      "この方向は手作業での補完が必要")

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

                f_abst = f.get("abstract") or ""

                rows.append({
                    "seed_id": seed["id"],
                    "seed_title": seed["title"],
                    "direction": direction,
                    "found_title": f_title,
                    "found_abstract": f_abst,
                    "found_doi": norm_doi(f_doi),
                    "found_year": f.get("year") or "",
                    "found_venue": venue,
                    "in_db_already": in_db,
                    "venue_rank_note": note,
                    "ref_source": src,
                    **kw_flags(f_title, f_abst),
                    "picos_decision": "",  # 著者記入
                    "reason": "",          # 著者記入
                })

    out_path = ROOT / "outputs" / "snowballing_log.csv"
    is_new = not out_path.exists()
    fieldnames = ["seed_id", "seed_title", "direction", "found_title", "found_abstract",
                  "found_doi", "found_year", "found_venue", "in_db_already", "venue_rank_note",
                  "ref_source", "kw_g1", "kw_g2", "kw_g3", "kw_groups",
                  "picos_decision", "reason"]

    # 追記モードなので、既存ファイルの列構成が変わっていたら**黙って壊さず中断する**。
    # (2026-08-10 に found_abstract / kw_* 列を追加したため、旧12列のログには追記できない)
    if not is_new:
        with out_path.open(encoding="utf-8-sig", newline="") as f:
            old = next(csv.reader(f), [])
        if old != fieldnames:
            sys.exit(
                f"[ERROR] 既存の {out_path.name} は列構成が古いため追記できません。\n"
                f"        旧 {len(old)} 列 / 新 {len(fieldnames)} 列"
                f"(追加: found_abstract, kw_g1..g3, kw_groups)\n"
                f"        旧ログを退避してから再実行してください:\n"
                f"          mv outputs/snowballing_log.csv outputs/snowballing_log_pre20260810.csv")

    with out_path.open("a", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if is_new:
            w.writeheader()
        w.writerows(rows)

    new_candidates = [r for r in rows if r["in_db_already"] == "N"]
    print(f"\n[INFO] 追記 {len(rows)} 件(うち既存コーパスに無い新規候補 {len(new_candidates)} 件)")
    if new_candidates:
        print("[INFO] 新規候補の概念群(Title+Abstract、読む順序のトリアージ用):")
        for g in (3, 2, 1, 0):
            n = sum(1 for r in new_candidates if r["kw_groups"] == g)
            print(f"          {g}群成立: {n:5d} 件")
        noabs = sum(1 for r in new_candidates if not r["found_abstract"].strip())
        print(f"       ※ 要旨を取得できなかったもの {noabs} 件(kw_* は過小評価になる)")
    print(f"[INFO] 出力: {out_path}")
    print("[NEXT] kw_groups の降順に読み、picos_decision 列に include/exclude、"
          "reason 列に理由を著者が記入すること。")
    print("       kw_groups は**順序付け専用**。これで機械的に除外する場合は"
          "逸脱として PRISMA-S に明記すること(docs/snowballing_protocol.md §4.3/§4.6)。")


if __name__ == "__main__":
    main()
