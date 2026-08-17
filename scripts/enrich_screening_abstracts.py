#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enrich_screening_abstracts.py — Phase 3b 判定対象の要旨を DOI から補完する
================================================================================

⚠️ **外部 API に通信する**(Crossref / Semantic Scholar)。著者の指示があるときだけ実行する。

【何を】
Phase 3b の判定対象(`screening/assignment.csv` の全レコード)のうち **要旨が無いもの**に
ついて、DOI をキーに要旨を取得し、`outputs/enriched_abstracts.csv` にキャッシュする。
判定シートの生成時(`make_screening_sheets.py`)にこのキャッシュが参照される。

【なぜ独立した工程にするか】
シートを直接書き換えると、シートを再生成したときに補完が消える。補完を
**DOI をキーにした再利用可能なキャッシュ**として外に置けば、シートを何度作り直しても残る。
また「どの要旨が外部由来か」を出所つきで保持でき、PRISMA-S に報告できる。

【★重要: 補完した要旨で自動除外を掛け直さないこと】
補完は **人手判定(Phase 3b)を助けるため**に行う。既に「判定不能なので人手に委ねる」と
決めたレコード(Phase 1.5 の `hold`)について、その決定を機械側に巻き戻すためではない。

理由:
  - PRISMA 2020 は自動ツールによる除外を "Records marked as ineligible by automation tools"
    として**スクリーニングの手前**に置き、人手除外とは**分けて報告する**ことを求めている。
    補完後に Phase 1.5 / Phase 3a を再適用すると、検索が一度も見ていないテキストで
    自動除外が発動することになる。
  - Phase 1.5 のフェイルセーフは「メタデータが欠けているから除外」を避けるためのもの。
    再適用は「メタデータが後から手に入ったから除外」となり、目的と逆行する。
  - 文献が残るかどうかが **Semantic Scholar のカバレッジ**に左右されてしまう。
  - 「外部APIで補完したテキストに自動除外を掛け直す」運用の前例は確認できていない
    (メタデータ補完自体と、自動ツールによる除外は、それぞれ単独では標準的な運用)。

したがって本スクリプトは **`Abstract Note` 相当の内容をキャッシュするだけ**で、
パイプライン(`pipeline.py`)の入力も step ファイルも一切書き換えない。

【入出力】
  入力: screening/assignment.csv(判定対象の DOI 一覧)
        step3_kw_included.csv / outputs/snowballing_log.csv(既存の要旨の有無を見る)
  出力: outputs/enriched_abstracts.csv
        列: doi, abstract, source, chars, fetched_at
        source は crossref / semantic_scholar / notfound(要旨が存在しない) /
        ratelimited(レート制限で取れなかった。次回実行で自動再試行される)

実行:
  python -X utf8 scripts/enrich_screening_abstracts.py --limit 50   # 試験
  python -X utf8 scripts/enrich_screening_abstracts.py              # 本実行
  python -X utf8 scripts/enrich_screening_abstracts.py --retry-notfound
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from datetime import date
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(_HERE))

csv.field_size_limit(10 ** 9)

from api_search_common import load_dotenv  # noqa: E402
from enrich_abstracts import fetch_crossref, norm_doi  # noqa: E402

load_dotenv()

try:
    import requests
except ImportError:
    sys.exit("[ERROR] requests が必要です:  pip install requests")

OUT_COLS = ["doi", "abstract", "source", "chars", "fetched_at"]

S2_URL = "https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=abstract"

# Semantic Scholar は 429(レート制限)を返す。**「本当に要旨が無い(200 + abstract:null)」と
# 「レート制限で取れなかった(429)」を区別する**ことが重要で、両方を notfound にまとめると
# 「要旨が存在しない」という誤った記録が残り、再試行の機会も失われる。
# 実際、初回の本実行では S2 の取得数が74件で頭打ちになり、以降はすべて 429 だった
# (共有の `enrich_abstracts._get` のバックオフ 0.5→1→2秒では 429 に対して短すぎる)。
S2_BACKOFF = [2, 5, 15, 40]   # 秒


def fetch_s2_status(doi: str, api_key: str | None) -> tuple[str, str]:
    """(要旨, 状態) を返す。状態は 'ok' / 'empty'(要旨が無い) / 'ratelimited' / 'error'。"""
    headers = {"x-api-key": api_key} if api_key else {}
    for wait in [0] + S2_BACKOFF:
        if wait:
            time.sleep(wait)
        try:
            resp = requests.get(S2_URL.format(doi=doi), headers=headers, timeout=30)
        except requests.RequestException:
            continue
        if resp.status_code == 200:
            try:
                a = (resp.json().get("abstract") or "").strip()
            except ValueError:
                return "", "error"
            return (a, "ok") if a else ("", "empty")
        if resp.status_code in (429, 500, 502, 503, 504):
            continue
        return "", "error"          # 404 等は再試行しない
    return "", "ratelimited"


def load_existing_abstracts() -> dict[str, str]:
    """判定対象の DOI → 既存の要旨(空文字なら欠落)。"""
    have: dict[str, str] = {}
    p = ROOT / "step3_kw_included.csv"
    if p.exists():
        with p.open(encoding="utf-8-sig", newline="", errors="replace") as f:
            for r in csv.DictReader(f):
                d = norm_doi(r.get("DOI", ""))
                if d:
                    have[d] = (r.get("Abstract Note") or "").strip()
    p = ROOT / "outputs" / "snowballing_log.csv"
    if p.exists():
        with p.open(encoding="utf-8-sig", newline="", errors="replace") as f:
            for r in csv.DictReader(f):
                if r.get("in_db_already") != "N":
                    continue
                d = norm_doi(r.get("found_doi", ""))
                if d and d not in have:
                    have[d] = (r.get("found_abstract") or "").strip()
    return have


def load_cache(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        return {r["doi"]: r for r in csv.DictReader(f) if r.get("doi")}


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 3b 判定対象の要旨を DOI から補完")
    ap.add_argument("--assignment", type=Path, default=ROOT / "screening" / "assignment.csv")
    ap.add_argument("--out", type=Path, default=ROOT / "outputs" / "enriched_abstracts.csv")
    ap.add_argument("--limit", type=int, default=0, help="処理上限(0=無制限)。試験に使う")
    ap.add_argument("--retry-notfound", action="store_true",
                    help="前回 notfound だった DOI も再試行する")
    args = ap.parse_args()

    if not args.assignment.exists():
        sys.exit(f"[ERROR] {args.assignment} がありません。"
                 f"先に make_screening_sheets.py を実行すること")

    with args.assignment.open(encoding="utf-8-sig", newline="") as f:
        targets = [r for r in csv.DictReader(f)]
    have = load_existing_abstracts()
    cache = load_cache(args.out)

    todo = []
    no_doi = 0
    for r in targets:
        d = norm_doi(r.get("doi", ""))
        if not d:
            no_doi += 1
            continue
        if have.get(d):                      # 既に要旨がある
            continue
        c = cache.get(d)
        if c:
            # ratelimited は「取れなかった」だけなので**常に**再試行の対象にする。
            # notfound(要旨が存在しない)は --retry-notfound を付けたときだけ。
            if c["source"] == "ratelimited":
                pass
            elif c["source"] != "notfound" or not args.retry_notfound:
                continue
        todo.append(d)

    print(f"[INFO] 判定対象 {len(targets):,} 件")
    print(f"       要旨あり(補完不要)          : {sum(1 for r in targets if have.get(norm_doi(r.get('doi',''))))}")
    print(f"       DOI が無く照会できない       : {no_doi}")
    print(f"       キャッシュ済み               : {len(cache):,}")
    print(f"       → 今回照会する DOI          : {len(todo):,}")
    if args.limit:
        todo = todo[:args.limit]
        print(f"       (--limit {args.limit} により先頭 {len(todo)} 件のみ)")
    if not todo:
        print("[INFO] 照会対象なし。終了。")
        return

    mailto = os.environ.get("ENRICH_MAILTO", "")
    s2key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY") or os.environ.get("S2_API_KEY")
    if not mailto:
        print("[WARN] ENRICH_MAILTO 未設定。Crossref の polite pool を使えない")

    got = {"crossref": 0, "semantic_scholar": 0, "notfound": 0, "ratelimited": 0}
    for i, doi in enumerate(todo, 1):
        text = fetch_crossref(doi, mailto)
        src = "crossref"
        if not text:
            text, st = fetch_s2_status(doi, s2key)
            # 'empty'(要旨が存在しない)と 'ratelimited'(取れなかった)を区別して記録する。
            # ratelimited は次回実行で自動的に再試行される。
            src = ("semantic_scholar" if st == "ok"
                   else "ratelimited" if st == "ratelimited" else "notfound")
        got[src] += 1
        cache[doi] = {"doi": doi, "abstract": text or "", "source": src,
                      "chars": len(text or ""), "fetched_at": date.today().isoformat()}
        if i % 25 == 0 or i == len(todo):
            ok = got["crossref"] + got["semantic_scholar"]
            print(f"    {i:>5}/{len(todo)}  取得 {ok}  "
                  f"(Crossref {got['crossref']} / S2 {got['semantic_scholar']})  "
                  f"要旨なし {got['notfound']} / レート制限 {got['ratelimited']}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_COLS)
        w.writeheader()
        for d in sorted(cache):
            w.writerows([{k: cache[d].get(k, "") for k in OUT_COLS}])

    ok = got["crossref"] + got["semantic_scholar"]
    n = len(todo)
    print(f"\n[INFO] 照会 {n} 件 → 取得 {ok} 件 ({ok / n * 100:.0f}%)")
    print(f"       Crossref {got['crossref']} / Semantic Scholar {got['semantic_scholar']}")
    print(f"       要旨が存在しない {got['notfound']} / レート制限で未取得 {got['ratelimited']}")
    if got["ratelimited"]:
        print("       ★ レート制限分は再実行すれば取得できる可能性がある")
    print(f"[INFO] 出力: {args.out}  (累計 {len(cache):,} 件)")
    print("[NEXT] `python -X utf8 scripts/make_screening_sheets.py` でシートに反映する。")
    print("       ★ 補完した要旨で Phase 1.5 / Phase 3a を再適用してはならない")
    print("         (人手判定の材料としてのみ使う。理由は本スクリプトのヘッダ)。")


if __name__ == "__main__":
    main()
