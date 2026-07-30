#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
db_search_scopus.py — Scopus Search API による自動検索(Rev.6 第2波再検索用)
================================================================================

⚠️ 本スクリプトは **外部 API に通信する**。方針(既存の制約)により Claude は
   実行しない。**著者が手元環境で実行する**こと。ここではコードと手順のみ整備する。

【背景 / なぜ】
`protocol_changelog.md` Rev.8 で DB構成を ACM/IEEE/Scopus の3DBに確定。Scopus は
特に、known-item の心理系文献(#5/#6/#14)を捕捉し、#10 の唯一の情報源でもある
最重要DB(`docs/methodology_decision_Rev7.md` §B)。本スクリプトは Scopus 分の
第2波再検索(Rev.6 G1拡張クエリ)を Scopus Search API 経由で自動化する。
副産物として、Rev.7 §D で欠陥として特定された **Author/Index Keywords の欠落(1.2%)**
を、`view=COMPLETE` 指定によりできる範囲で補う(entitlement 次第、下記参照)。

【前提・取得方法】
1. https://dev.elsevier.com/ でアカウント登録し、API キーを取得(無料)。
2. Abstract・Keywords まで取得するには `view=COMPLETE` が必要で、多くの場合
   **所属機関のIP範囲からのアクセス、または Institutional Token(insttoken)** が要る。
   キーのみ(institutional token 無し)の場合、`view=STANDARD` 相当の書誌情報
   (タイトル・著者・年・DOI・誌名)のみ返り、Abstract/Keywords は空になることが多い。
   その場合は `search_replication.md` §欠陥1/2 のとおり、別途 Abstract補完
   (`scripts/enrich_abstracts.py`)や手動エクスポートを検討する。
3. 環境変数 `SCOPUS_API_KEY`(必須)、`SCOPUS_INSTTOKEN`(任意、機関トークンがあれば)。

【使い方】
  export SCOPUS_API_KEY="..."
  export SCOPUS_INSTTOKEN="..."   # 任意
  # (a) Rev.6 既定クエリ(scope=TITLE-ABS、Rev.7運用ルール準拠)
  python -X utf8 scripts/db_search_scopus.py --use-default-query
  # (b) Keyword を含めて検索したい場合(scopeの逸脱。search_strings.md に明記が必要)
  python -X utf8 scripts/db_search_scopus.py --use-default-query --scope TITLE-ABS-KEY
  # (c) 手動で verbatim クエリを指定
  python -X utf8 scripts/db_search_scopus.py --query 'TITLE-ABS(("virtual reality" OR ...) AND (...))'
  # まず件数だけ:
  python -X utf8 scripts/db_search_scopus.py --use-default-query --count-only

【出力】
  raw/scopus_wave2_YYYYMMDD.ris        Zotero にインポートする RIS ファイル
  outputs/api_search_log.csv           実行記録(1行追記)

【ページングの注意(Scopus 仕様)】
Scopus Search API は `start + count` の合計が 5,000 を超えると通常のオフセット
ページングが使えず、カーソルベース(`cursor=*` → レスポンスの `cursor.@next` を
次リクエストに使う)に切り替える必要がある。本スクリプトはこれを自動判定して
切り替える(5,000件を境に自動でカーソルモードへ)。

【注意】
- レスポンス JSON のキー名(`dc:title` 等、Dublin Core 由来の記法)は Scopus API の
  安定仕様だが、`view` により含まれるフィールドが変わる。**少数件で試験実行し、
  Title/Abstract/DOI/Keywords が正しく入っているか確認してから本実行すること。**
- 既存 raw/Scopus.csv は上書きしない(別名で出力)。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent

from api_search_common import (  # noqa: E402
    CONCEPT_GROUPS_REV6,
    SearchRecord,
    build_scopus_query,
    polite_get,
    write_ris,
    append_hit_log,
    today_stamp,
    load_dotenv,
)

load_dotenv()  # SurveyProtocol/.env があれば読み込む(未 export の変数のみ補完)

BASE_URL = "https://api.elsevier.com/content/search/scopus"
MAX_COUNT_PER_CALL = 25          # view=COMPLETE 時の実務上の上限(entitlement依存)
CURSOR_THRESHOLD = 5000          # これを超えたら cursor モードに切替


def map_entry_to_record(entry: dict) -> SearchRecord:
    """Scopus Search API の1エントリ(dict)を SearchRecord に変換する。"""
    creator = entry.get("dc:creator") or ""
    authors = [creator] if creator else []

    agg_type = (entry.get("prism:aggregationType") or "").lower()
    is_conference = agg_type in ("conference proceeding", "conference")

    keywords_raw = entry.get("authkeywords") or ""
    keywords = [k.strip() for k in keywords_raw.split("|") if k.strip()] if keywords_raw else []

    return SearchRecord(
        title=entry.get("dc:title") or "",
        abstract=entry.get("dc:description") or "",  # view=COMPLETE + entitlement が要る
        venue=entry.get("prism:publicationName") or "",
        year=(entry.get("prism:coverDate") or "")[:4],
        doi=entry.get("prism:doi") or "",
        issn=entry.get("prism:issn") or entry.get("prism:eIssn") or "",
        url=next((l.get("@href", "") for l in (entry.get("link") or [])
                  if l.get("@ref") == "scopus"), ""),
        authors=authors,
        keywords=keywords,
        is_conference=is_conference,
    )


def _headers(api_key: str, insttoken: str | None) -> dict:
    h = {"X-ELS-APIKey": api_key, "Accept": "application/json"}
    if insttoken:
        h["X-ELS-Insttoken"] = insttoken
    return h


def search(query: str, api_key: str, insttoken: str | None, view: str,
           limit: int, count_only: bool) -> tuple[int, list[SearchRecord]]:
    """start/count オフセットで開始し、5,000件超で cursor モードへ自動切替。"""
    headers = _headers(api_key, insttoken)
    records: list[SearchRecord] = []
    total = 0
    start = 0
    cursor: str | None = None

    while True:
        params = {
            "query": query,
            "view": view,
            "count": 1 if count_only else min(MAX_COUNT_PER_CALL, limit - len(records)),
        }
        if cursor:
            params["cursor"] = cursor
        else:
            params["start"] = start

        resp = polite_get(BASE_URL, params=params, headers=headers)
        if resp is None or resp.status_code != 200:
            status = resp.status_code if resp is not None else "no response"
            body = resp.text[:300] if resp is not None else ""
            sys.exit(f"[ERROR] Scopus API 呼び出し失敗(status={status})。{body}\n"
                     "APIキー/Insttoken・クエリ構文・view の entitlement を確認してください。")

        data = resp.json().get("search-results", {})
        total = int(data.get("opensearch:totalResults", 0))
        if count_only:
            return total, []

        entries = data.get("entry") or []
        # Scopus は該当0件でも1件のダミーエントリ({"error": "Result set was empty"})を返すことがある
        entries = [e for e in entries if "dc:title" in e]
        if not entries:
            break
        records.extend(map_entry_to_record(e) for e in entries)

        if len(records) >= limit or len(records) >= total:
            break

        start += len(entries)
        if start >= CURSOR_THRESHOLD or cursor:
            # cursor モードへ切替 / 継続。次カーソルは応答内の cursor.@next
            next_cursor = (data.get("cursor") or {}).get("@next")
            if not next_cursor:
                break
            cursor = next_cursor

    return total, records


def main() -> None:
    ap = argparse.ArgumentParser(description="Scopus Search API 検索(著者実行用)")
    ap.add_argument("--query", type=str, default=None,
                    help="verbatim クエリ(手動指定)。省略時は --use-default-query が必要")
    ap.add_argument("--use-default-query", action="store_true",
                    help="build_scopus_query() の既定値(Rev.6 コンセプト群)を使用")
    ap.add_argument("--scope", type=str, default="TITLE-ABS",
                    choices=["TITLE-ABS", "TITLE-ABS-KEY"],
                    help="既定 TITLE-ABS(Rev.7運用ルール準拠)。KEY拡張はscope逸脱につき要記録")
    ap.add_argument("--view", type=str, default="COMPLETE",
                    choices=["STANDARD", "COMPLETE"],
                    help="COMPLETE で Abstract/Keywords 取得を試みる(entitlement次第)")
    ap.add_argument("--limit", type=int, default=5000,
                    help="総取得件数の安全上限(既定 5000)")
    ap.add_argument("--count-only", action="store_true",
                    help="ヒット件数のみ表示して終了(RIS出力なし)")
    ap.add_argument("--out", type=Path, default=None,
                    help="出力RISパス(既定: raw/scopus_wave2_YYYYMMDD.ris)")
    args = ap.parse_args()

    api_key = os.environ.get("SCOPUS_API_KEY")
    if not api_key:
        sys.exit("[ERROR] 環境変数 SCOPUS_API_KEY が未設定です。")
    insttoken = os.environ.get("SCOPUS_INSTTOKEN")

    if args.query:
        query = args.query
    elif args.use_default_query:
        query = build_scopus_query(CONCEPT_GROUPS_REV6, scope=args.scope)
        print(f"[INFO] 生成クエリ:\n{query}\n")
        print("[INFO] ↑ このクエリを docs/search_strings.md に verbatim として転記すること。")
    else:
        sys.exit("[ERROR] --query か --use-default-query のどちらかを指定してください。")

    if args.scope == "TITLE-ABS-KEY":
        print("[WARN] TITLE-ABS-KEY は実効scope=TAの方針(Rev.7)からの逸脱。"
              "search_strings.md にその旨を明記すること。")

    filters = f"view={args.view}"
    total, records = search(query, api_key, insttoken, args.view, args.limit, args.count_only)
    print(f"[INFO] total_records = {total}")
    if args.count_only:
        return

    out_path = args.out or (ROOT / "raw" / f"scopus_wave2_{today_stamp()}.ris")
    write_ris(records, out_path)
    print(f"[INFO] 取得 {len(records)} / 総 {total} 件を出力: {out_path}")
    if len(records) < total:
        print(f"[WARN] --limit({args.limit}) により総件数に達していません。"
              "必要なら --limit を上げて再実行してください。")

    no_abstract = sum(1 for r in records if not r.abstract)
    if records and no_abstract / len(records) > 0.5:
        print(f"[WARN] Abstract 欠落率が高い({no_abstract}/{len(records)})。"
              "view=COMPLETE の entitlement(機関アクセス/Insttoken)が無い可能性が高い。"
              "docs/search_replication.md §欠陥1/2 のフォールバック手順を参照。")

    log_path = append_hit_log("Scopus(第2波)", query, args.scope, filters,
                               total, len(records), str(out_path))
    print(f"[INFO] 実行記録: {log_path}")
    print("[NEXT] Zotero: ファイル→インポート→上記 .ris を選択し、専用コレクション"
          "(例: scopus_wave2)へ取り込む。取り込み後 docs/search_strings.md を更新すること。")


if __name__ == "__main__":
    main()
