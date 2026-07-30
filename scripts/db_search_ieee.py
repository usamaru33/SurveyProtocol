#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
db_search_ieee.py — IEEE Xplore Metadata API による自動検索(Rev.6 第2波再検索用)
================================================================================

⚠️ 本スクリプトは **外部 API に通信する**。方針(既存の制約)により Claude は
   実行しない。**著者が手元環境で実行する**こと。ここではコードと手順のみ整備する。

【背景 / なぜ】
`protocol_changelog.md` Rev.8 で DB構成を ACM/IEEE/Scopus の3DBに確定。
`docs/rule.md` Rev.6 で G1 拡張クエリが確定済みだが、実際の再検索(第2波)はまだ
実施されていない(`docs/PROGRESS_LOG.md` 次回やること#3)。本スクリプトは
IEEE Xplore 分の再検索を IEEE Xplore Metadata API 経由で自動化する。

【前提・取得方法】
1. https://developer.ieee.org/ でアカウント登録し、Metadata API の API キーを取得
   (無料枠: 200 call/day、1 call = 最大200件)。
2. 環境変数 `IEEE_API_KEY` に設定する。
3. verbatim クエリは `scripts/api_search_common.py` の `build_ieee_querytext()` で
   生成するか、著者が Command Search 構文で直接指定する。
   **生成後は必ず結果の文字列を `docs/search_strings.md` に verbatim として転記すること**
   (`docs/search_strings.md` Rev.7 運用ルール: フィールドは "Document Title":/"Abstract":、
   "All Metadata" は使わない)。

【使い方】
  export IEEE_API_KEY="..."
  # (a) Rev.6 既定クエリで実行(build_ieee_querytext の既定値を使用)
  python -X utf8 scripts/db_search_ieee.py --use-default-query
  # (b) 手動で verbatim クエリを指定する場合
  python -X utf8 scripts/db_search_ieee.py --query '("Document Title":"Virtual Reality" OR ...) AND (...)'
  # 年で絞る場合(Rev.3 の更新検索のように期間限定するなら):
  python -X utf8 scripts/db_search_ieee.py --use-default-query --start-year 2025 --end-year 2026
  # まず件数だけ見たい場合:
  python -X utf8 scripts/db_search_ieee.py --use-default-query --count-only

【出力】
  raw/ieee_wave2_YYYYMMDD.ris          Zotero にインポートする RIS ファイル
                                       (Zotero: ファイル→インポート→この .ris を選択、
                                        「IEEE_wave2」等の専用コレクションへ)
  outputs/api_search_log.csv           実行記録(1行追記。search_strings.md への転記下書き)

【注意】
- IEEE の JSON レスポンスのフィールド名は API バージョンにより変動しうる。
  本スクリプトは `.get()` で欠損に耐性があるが、**少数件(--limit 10 等)で試験実行し、
  Title/Abstract/DOI/Year が正しく入っているか目視確認してから本実行すること。**
- 無料枠 200 call/day、1 call 最大200件 = 理論上 40,000件/day だが、実際のクォータは
  変更されうる。`--limit` で総取得件数に安全上限をかけている(既定 5,000)。
- 既存 raw/ieee.csv・raw/IEEE_2025-2026.csv は上書きしない(別名で出力)。
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
    build_ieee_querytext,
    polite_get,
    write_ris,
    append_hit_log,
    today_stamp,
    load_dotenv,
)

load_dotenv()  # SurveyProtocol/.env があれば読み込む(未 export の変数のみ補完)

BASE_URL = "http://ieeexploreapi.ieee.org/api/v1/search/articles"
MAX_RECORDS_PER_CALL = 200


def map_article_to_record(article: dict) -> SearchRecord:
    """IEEE Xplore API の1レコード(dict)を SearchRecord に変換する。

    フィールド名は IEEE Xplore Metadata API v1 の公開ドキュメントに基づく想定値。
    レスポンスの実際のキーが違う場合はここを修正すること(--limit 10 で試験実行し確認)。
    """
    authors_obj = article.get("authors") or {}
    author_list = authors_obj.get("authors") or []
    authors = [a.get("full_name", "") for a in author_list if a.get("full_name")]

    content_type = (article.get("content_type") or "").lower()
    is_conference = "conference" in content_type or "proceeding" in content_type

    return SearchRecord(
        title=article.get("title") or article.get("article_title") or "",
        abstract=article.get("abstract") or "",
        venue=article.get("publication_title") or "",
        year=str(article.get("publication_year") or ""),
        doi=article.get("doi") or "",
        issn=article.get("issn") or "",
        url=article.get("html_url") or article.get("pdf_url") or "",
        authors=authors,
        keywords=[],  # IEEE Metadata API の索引語は index_terms 配下(必要なら別途対応)
        is_conference=is_conference,
    )


def search(query: str, api_key: str, start_year: str | None, end_year: str | None,
           limit: int, count_only: bool) -> tuple[int, list[SearchRecord]]:
    """ページングしながら全件取得する。戻り値: (total_records, records)。"""
    records: list[SearchRecord] = []
    start_record = 1
    total = 0
    while True:
        params = {
            "apikey": api_key,
            "querytext": query,
            "start_record": start_record,
            "max_records": 1 if count_only else min(MAX_RECORDS_PER_CALL, limit - len(records)),
            "format": "json",
        }
        if start_year:
            params["start_year"] = start_year
        if end_year:
            params["end_year"] = end_year

        resp = polite_get(BASE_URL, params=params)
        if resp is None or resp.status_code != 200:
            status = resp.status_code if resp is not None else "no response"
            sys.exit(f"[ERROR] IEEE API 呼び出し失敗(status={status})。"
                     f"APIキー・クエリ構文を確認してください。")

        data = resp.json()
        total = data.get("total_records", 0)
        if count_only:
            return total, []

        articles = data.get("articles") or []
        if not articles:
            break
        records.extend(map_article_to_record(a) for a in articles)

        if len(records) >= limit or len(records) >= total:
            break
        start_record += len(articles)

    return total, records


def main() -> None:
    ap = argparse.ArgumentParser(description="IEEE Xplore Metadata API 検索(著者実行用)")
    ap.add_argument("--query", type=str, default=None,
                    help="verbatim querytext(手動指定)。省略時は --use-default-query が必要")
    ap.add_argument("--use-default-query", action="store_true",
                    help="build_ieee_querytext() の既定値(Rev.6 コンセプト群)を使用")
    ap.add_argument("--start-year", type=str, default=None)
    ap.add_argument("--end-year", type=str, default=None)
    ap.add_argument("--limit", type=int, default=5000,
                    help="総取得件数の安全上限(既定 5000)")
    ap.add_argument("--count-only", action="store_true",
                    help="ヒット件数のみ表示して終了(RIS出力なし)")
    ap.add_argument("--out", type=Path, default=None,
                    help="出力RISパス(既定: raw/ieee_wave2_YYYYMMDD.ris)")
    args = ap.parse_args()

    api_key = os.environ.get("IEEE_API_KEY")
    if not api_key:
        sys.exit("[ERROR] 環境変数 IEEE_API_KEY が未設定です。")

    if args.query:
        query = args.query
        fields_desc = "verbatim(手動指定)"
    elif args.use_default_query:
        query = build_ieee_querytext(CONCEPT_GROUPS_REV6, fields=("Document Title", "Abstract"))
        fields_desc = "Document Title, Abstract"
        print(f"[INFO] 生成クエリ:\n{query}\n")
        print("[INFO] ↑ このクエリを docs/search_strings.md に verbatim として転記すること。")
    else:
        sys.exit("[ERROR] --query か --use-default-query のどちらかを指定してください。")

    filters = f"start_year={args.start_year or '-'}, end_year={args.end_year or '-'}"

    total, records = search(query, api_key, args.start_year, args.end_year,
                             args.limit, args.count_only)
    print(f"[INFO] total_records = {total}")
    if args.count_only:
        return

    out_path = args.out or (ROOT / "raw" / f"ieee_wave2_{today_stamp()}.ris")
    write_ris(records, out_path)
    print(f"[INFO] 取得 {len(records)} / 総 {total} 件を出力: {out_path}")
    if len(records) < total:
        print(f"[WARN] --limit({args.limit}) により総件数に達していません。"
              "必要なら --limit を上げて再実行してください。")

    log_path = append_hit_log("IEEE Xplore(第2波)", query, fields_desc, filters,
                               total, len(records), str(out_path))
    print(f"[INFO] 実行記録: {log_path}")
    print("[NEXT] Zotero: ファイル→インポート→上記 .ris を選択し、専用コレクション"
          "(例: ieee_wave2)へ取り込む。取り込み後 docs/search_strings.md を更新すること。")


if __name__ == "__main__":
    main()
