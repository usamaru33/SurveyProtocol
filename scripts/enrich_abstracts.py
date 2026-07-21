#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enrich_abstracts.py — DOI ベースの Abstract 補完(ACM の Abstract 欠落是正)
================================================================================

⚠️ 本スクリプトは **外部 API に通信する**。方針(Rev.7 制約)により、Claude は
   実行しない。**著者が手元環境で実行する**こと。ここではコードと手順のみ整備する。

【背景 / なぜ】
methodology_decision_Rev7.md §D の実測: ACM の raw エクスポートは Abstract が
**4.3%(342/7,997)しか無い**。フィルタ層(方針3)で Title-Abstract(TA)スコープを
再適用するには ACM レコードに Abstract が必要。ACM DL からの再エクスポートで
Abstract が取れれば本スクリプトは不要(search_replication.md「Rev.7 エクスポート
欠陥の是正」を先に試すこと)。**再エクスポートで取れない場合のフォールバック**が本器。

【何を】
Abstract が空のレコードについて、DOI をキーに以下のソースから Abstract を取得し、
`Abstract Note` 列を埋めた新しい CSV を書き出す(元ファイルは上書きしない)。
  1. Crossref REST API (https://api.crossref.org/works/{DOI})  … `abstract`(JATS/XML)
  2. Semantic Scholar Graph API                                … `abstract`(平文、fallback)
両方とも DOI 単位のルックアップで、著者名・メールを含む polite User-Agent を送る。

【使い方(著者が実行)】
  # 依存: requests(標準ライブラリのみで動かすなら urllib 版に置換可)
  #   pip install requests
  export ENRICH_MAILTO="you@example.com"        # Crossref polite pool 用(必須推奨)
  export S2_API_KEY="..."                        # 任意(あればレート制限が緩む)
  python -X utf8 scripts/enrich_abstracts.py \
      --in raw/acm.csv --out raw/acm_enriched.csv [--only-empty] [--limit N]

【出力】
  --out で指定した CSV(入力と同一スキーマ + Abstract Note を補完)。
  併せて outputs/enrich_abstracts_report.csv に DOI 単位の取得結果
  (source / status / chars)を記録する。

【設計上の注意】
  - **決定論性**: 取得元の優先順位は Crossref → S2 固定。同じ DOI には同じ結果。
  - **礼儀正しい通信**: 既定 0.5 秒/リクエストのスリープ。429/5xx は指数バックオフで最大3回。
  - **非改変**: 入力レコードは Abstract Note 以外の列を一切変更しない。
  - **監査可能性**: どの Abstract をどのソースから補完したかを report に必ず残す
    (PRISMA / 再現性のため。本文に「ACM Abstract の X 件を Crossref/S2 で補完」と記載できる)。
  - **JATS 除去**: Crossref の abstract は <jats:p> 等のタグを含むため簡易に除去する。

本スクリプトは step ファイルを変更しない。ACM の生データ(raw/acm.csv)も上書きせず、
別名(acm_enriched.csv)で出す。統合パイプラインへの反映は著者判断。
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests  # type: ignore
except ImportError:
    requests = None  # 実行時にのみ必須。整備段階では未インストールでも読める。

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent

CROSSREF = "https://api.crossref.org/works/"
S2 = "https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=abstract"
SLEEP = 0.5
MAX_RETRY = 3


def norm_doi(raw: str) -> str:
    d = (raw or "").strip().lower()
    d = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    return d


def strip_jats(text: str) -> str:
    """Crossref abstract の JATS/XML タグを除去して平文化する。"""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)          # タグ除去
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"^\s*abstract\s*", "", text, flags=re.I).strip()


def _get(url: str, headers: dict) -> "requests.Response | None":
    """指数バックオフ付き GET。requests 前提。"""
    delay = SLEEP
    for attempt in range(1, MAX_RETRY + 1):
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp
        if resp.status_code in (429, 500, 502, 503, 504):
            time.sleep(delay)
            delay *= 2
            continue
        return None
    return None


def fetch_crossref(doi: str, mailto: str) -> str:
    headers = {"User-Agent": f"SelfScaleSurvey/1.0 (mailto:{mailto})"}
    resp = _get(CROSSREF + doi, headers)
    if not resp:
        return ""
    msg = resp.json().get("message", {})
    return strip_jats(msg.get("abstract", ""))


def fetch_s2(doi: str, api_key: str | None) -> str:
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    resp = _get(S2.format(doi=doi), headers)
    if not resp:
        return ""
    return (resp.json().get("abstract") or "").strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="DOI ベース Abstract 補完(著者実行用)")
    ap.add_argument("--in", dest="inp", type=Path, required=True)
    ap.add_argument("--out", dest="out", type=Path, required=True)
    ap.add_argument("--only-empty", action="store_true",
                    help="Abstract Note が空の行だけ補完する(推奨)")
    ap.add_argument("--limit", type=int, default=0, help="処理上限(0=無制限)")
    args = ap.parse_args()

    if requests is None:
        sys.exit("[ERROR] requests 未インストール。`pip install requests` 後に実行してください。")

    mailto = os.environ.get("ENRICH_MAILTO", "")
    if not mailto:
        print("[WARN] ENRICH_MAILTO 未設定。Crossref polite pool を使えず制限が厳しくなります。")
    s2_key = os.environ.get("S2_API_KEY")

    with args.inp.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    if "Abstract Note" not in fieldnames or "DOI" not in fieldnames:
        sys.exit("[ERROR] 入力に 'DOI' / 'Abstract Note' 列が必要です。")

    report: list[dict] = []
    processed = 0
    for r in rows:
        has_abs = bool((r.get("Abstract Note") or "").strip())
        if args.only_empty and has_abs:
            continue
        doi = norm_doi(r.get("DOI", ""))
        if not doi:
            report.append({"doi": "", "source": "-", "status": "no_doi", "chars": 0})
            continue
        if args.limit and processed >= args.limit:
            break
        processed += 1

        abstract = fetch_crossref(doi, mailto)
        source = "crossref"
        if not abstract:
            abstract = fetch_s2(doi, s2_key)
            source = "s2"
        time.sleep(SLEEP)

        if abstract:
            r["Abstract Note"] = abstract
            report.append({"doi": doi, "source": source, "status": "ok",
                           "chars": len(abstract)})
        else:
            report.append({"doi": doi, "source": "-", "status": "not_found", "chars": 0})

    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    rep_path = ROOT / "outputs" / "enrich_abstracts_report.csv"
    rep_path.parent.mkdir(exist_ok=True)
    with rep_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["doi", "source", "status", "chars"])
        w.writeheader()
        w.writerows(report)

    ok = sum(1 for x in report if x["status"] == "ok")
    print(f"[INFO] 補完成功 {ok} / 試行 {processed}。出力: {args.out}")
    print(f"[INFO] 監査ログ: {rep_path}(PRISMA/本文に補完件数とソースを記載すること)")


if __name__ == "__main__":
    main()
