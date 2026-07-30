#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
api_search_common.py — DB検索APIラッパー共通部品(IEEE Xplore / Scopus)
================================================================================

⚠️ 本モジュール自体はネットワーク通信を行わないが、これを使う
   `db_search_ieee.py` / `db_search_scopus.py` は外部APIに通信する。
   方針(既存の制約)により Claude は実行しない。著者が実行すること。

【何を】
Rev.6 で確定した G1 拡張クエリ(3コンセプト群)を、IEEE Xplore の Command Search
構文(フィールド接頭辞つき)と Scopus の `TITLE-ABS(...)` 構文の**両方に同一のコンセプト群
定義から機械的に変換**するビルダーを提供する。手で2DB分書き写すと表記が食い違う
(Rev.7/Rev.8 で問題になった「verbatim フィールド指定構文の不一致」)ため、
単一の定義から生成することで一致を保証する。

生成された文字列は必ず `search_strings.md` に**そのままコピー**して verbatim として
記録すること(このツールが生成した、で終わらせず、著者が確認のうえ記録する)。

【なぜ】
- `docs/search_strings.md` Rev.7 運用ルール: Scopus は `TITLE-ABS`(`TITLE-ABS-KEY` ではない)、
  IEEE は `"Document Title":`/`"Abstract":`(`"All Metadata"` ではない)を使うこと、と規定済み。
- `docs/protocol_changelog.md` Rev.8: DB構成は ACM/IEEE/Scopus の3DB。PubMed 不使用。
- 本モジュールはこの2点を踏まえた検索クエリ生成・実行・出力(RIS)を担う。

【提供する関数】
  CONCEPT_GROUPS_REV6         Rev.6 で確定したG1拡張後の3コンセプト群(既定値)
  build_ieee_querytext()      IEEE Command Search 用 querytext を生成
  build_scopus_query()        Scopus TITLE-ABS(...) クエリを生成
  polite_get()                429/5xx に指数バックオフで再試行する GET
  write_ris()                 検索結果を RIS ファイルに出力(Zotero 直接取り込み用)
  append_hit_log()            outputs/api_search_log.csv に実行記録を追記
                               (search_strings.md へ転記する際の下書きになる)

【出力を RIS にする理由】
既存の運用(`search_replication.md`)は「Zotero にDB別コレクションで取り込み→
CSVエクスポート」を前提にしている。RIS は Zotero が直接インポートできる標準形式であり、
この運用を変えずに新しい検索結果を合流させられる(生CSVを直接 raw/ に置いて
パイプラインへ流し込む方式は、Zotero 由来の raw/*.csv とスキーマの厳密な一致を
要求され脆いため採らない)。
"""

from __future__ import annotations

import csv
import time
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path

try:
    import requests  # type: ignore
except ImportError:
    requests = None  # 実行時にのみ必須(整備段階では未インストールでも読める)

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent

# ---------------------------------------------------------------------------
# Rev.6 確定クエリ(search_strings.md「Rev.6 改訂クエリ」と同一のコンセプト群)
# ---------------------------------------------------------------------------
CONCEPT_GROUPS_REV6: list[list[str]] = [
    ["Virtual Reality", "VR", "HMD", "head-mounted display",
     "head mounted display", "Virtual Environment*", "immersive virtual"],
    ["Avatar", "Body", "Embodiment"],
    ["Size", "Scale", "Height", "Distance"],
]


def build_ieee_querytext(
    concept_groups: list[list[str]] = CONCEPT_GROUPS_REV6,
    fields: tuple[str, ...] = ("Document Title", "Abstract"),
) -> str:
    """IEEE Xplore Command Search 用の querytext を生成する。

    各コンセプト群の各語を、指定フィールドすべてに対して OR 展開し、
    群同士は AND で結合する(rule.md / search_strings.md の Title+Abstract 対象と整合)。
    例(1群・1フィールドのみ簡略表示):
      ("Document Title":"Virtual Reality" OR "Abstract":"Virtual Reality" OR ...) AND (...) AND (...)

    ⚠️ IEEE の Command Search 構文・ワイルドカード(`*`)の挙動は API と Web UI で
       差異がありうる。**少数語での試験実行(--dry-run 相当)でヒット件数を確認してから
       本実行すること。**
    """
    group_clauses = []
    for group in concept_groups:
        terms = []
        for term in group:
            for fld in fields:
                terms.append(f'"{fld}":"{term}"')
        group_clauses.append("(" + " OR ".join(terms) + ")")
    return " AND ".join(group_clauses)


def build_scopus_query(
    concept_groups: list[list[str]] = CONCEPT_GROUPS_REV6,
    scope: str = "TITLE-ABS",
) -> str:
    """Scopus Search API 用のクエリを生成する(既定 scope=TITLE-ABS、Rev.7運用ルール準拠)。

    TITLE-ABS-KEY を使うと索引語(Keyword)にもマッチし scope が広がるため、
    実効scope=TA(Title-Abstract)の方針に合わせるなら既定の TITLE-ABS を使うこと。
    Keyword を意図的に含めたい場合のみ scope="TITLE-ABS-KEY" を指定し、
    その旨を search_strings.md に明記する。
    """
    group_clauses = ["(" + " OR ".join(f'"{term}"' for term in group) + ")"
                      for group in concept_groups]
    inner = " AND ".join(group_clauses)
    return f"{scope}({inner})"


# ---------------------------------------------------------------------------
# 礼儀正しい HTTP GET(指数バックオフ)
# ---------------------------------------------------------------------------

def polite_get(url: str, params: dict | None = None, headers: dict | None = None,
               retries: int = 5, base_delay: float = 1.0, timeout: int = 30):
    """429/5xx を指数バックオフで最大 retries 回再試行する GET。requests 必須。"""
    if requests is None:
        raise RuntimeError("requests 未インストール。`pip install requests` してください。")
    delay = base_delay
    last_resp = None
    for attempt in range(1, retries + 1):
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        last_resp = resp
        if resp.status_code == 200:
            return resp
        if resp.status_code in (429, 500, 502, 503, 504):
            time.sleep(delay)
            delay *= 2
            continue
        return resp  # 4xx (401/403等) は再試行しても無駄なので即返す
    return last_resp


# ---------------------------------------------------------------------------
# RIS 出力(Zotero 直接取り込み用)
# ---------------------------------------------------------------------------

@dataclass
class SearchRecord:
    """DB非依存の検索結果1件。DBごとのマッピング関数がこれを組み立てる。"""
    title: str = ""
    abstract: str = ""
    venue: str = ""
    year: str = ""
    doi: str = ""
    issn: str = ""
    url: str = ""
    authors: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    is_conference: bool = False  # True なら RIS TY=CONF、False なら JOUR


def _ris_escape(text: str) -> str:
    """RIS はタグ行区切りのため、値中の改行を除去するだけで足りる(タグ自体はエスケープ不要)。"""
    return (text or "").replace("\r", " ").replace("\n", " ").strip()


def write_ris(records: list[SearchRecord], out_path: Path) -> None:
    """検索結果を RIS ファイルに書き出す(Zotero: ファイル → インポート → この .ris を選択)。"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for r in records:
        lines.append(f"TY  - {'CONF' if r.is_conference else 'JOUR'}")
        if r.title:
            lines.append(f"TI  - {_ris_escape(r.title)}")
        if r.abstract:
            lines.append(f"AB  - {_ris_escape(r.abstract)}")
        if r.venue:
            tag = "T2" if r.is_conference else "JO"
            lines.append(f"{tag}  - {_ris_escape(r.venue)}")
        if r.year:
            lines.append(f"PY  - {_ris_escape(r.year)}")
        if r.doi:
            lines.append(f"DO  - {_ris_escape(r.doi)}")
        if r.issn:
            lines.append(f"SN  - {_ris_escape(r.issn)}")
        if r.url:
            lines.append(f"UR  - {_ris_escape(r.url)}")
        for a in r.authors:
            if a.strip():
                lines.append(f"AU  - {_ris_escape(a)}")
        for k in r.keywords:
            if k.strip():
                lines.append(f"KW  - {_ris_escape(k)}")
        lines.append("ER  - ")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# 実行記録ログ(search_strings.md への転記下書き)
# ---------------------------------------------------------------------------

def append_hit_log(db: str, query: str, fields_or_scope: str, filters: str,
                    hits_total: int, hits_fetched: int, out_file: str) -> Path:
    """outputs/api_search_log.csv に1行追記する(累積ログ、既存行は保持)。

    列は search_strings.md の「DB別記録表」と同じ並びにしてあるので、
    実行後この行を目視確認のうえ search_strings.md にコピーすること
    (このログをそのまま PRISMA 記録として使わない — 著者確認を経ること)。
    """
    log_path = ROOT / "outputs" / "api_search_log.csv"
    log_path.parent.mkdir(exist_ok=True)
    is_new = not log_path.exists()
    with log_path.open("a", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(["executed_at", "db", "search_string_verbatim",
                        "fields_or_scope", "filters", "hits_total",
                        "hits_fetched", "out_file"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), db, query,
                    fields_or_scope, filters, hits_total, hits_fetched, out_file])
    return log_path


def today_stamp() -> str:
    return date.today().strftime("%Y%m%d")


# ---------------------------------------------------------------------------
# .env 読み込み(APIキーを環境変数に手動 export しなくて済むように)
# ---------------------------------------------------------------------------

def load_dotenv(env_path: Path | None = None) -> None:
    """SurveyProtocol/.env を読み、未設定の環境変数のみ os.environ にセットする。

    `.env` は `.gitignore` で除外済み(絶対にコミットしない)。依存パッケージを増やさない
    ための簡易パーサ(`KEY=VALUE` 行のみ対応、コメント `#` と空行は無視)。
    既に環境変数として export 済みの値は上書きしない(明示的な export を優先)。
    """
    import os
    path = env_path or (ROOT / ".env")
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
