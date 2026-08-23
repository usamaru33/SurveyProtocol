#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""要旨の日本語訳をキャッシュに作る（閲覧アプリの対訳表示用）。

**訳文は判定の材料ではなく読解の補助である。** 閲覧アプリは常に原文を併記し、
訳文だけを表示する状態を既定にしない。理由:

  (1) 判定は原文に対して下すもの。機械翻訳は `head-mounted display` と
      `desktop display`、`patients` と `participants` のような**適格性を反転させる語**を
      取り違えうる。訳文だけで判定すると、その誤りが判定の誤りにそのまま化ける。
  (2) κ は校正セット(223件)で著者×各評価者について算出する。著者だけが訳文を読み、
      評価者が原文を読むと、**3名が別の刺激を判定している**ことになり、κ に
      翻訳のブレが混入する。訳を使うなら3名に同じものを配るか、使用を開示すること。

**再現性の担保:** 機械翻訳はエンジン・モデル・実行日で出力が変わる。そこで訳文は
JSON キャッシュに固定し、原文の SHA-1・エンジン名・実行日を各エントリに記録する。
**このキャッシュを supplementary material として公開すれば、著者が実際に読んだ
訳文を第三者が再現できる。** 再実行しても既存エントリは翻訳し直さない
（原文が変わったものだけ再取得する）。

使い方:
    # まず見積もり（通信しない）
    python -X utf8 scripts/translate_abstracts.py --estimate

    # 校正セットだけ翻訳（無料枠に収まる範囲から始める）
    python -X utf8 scripts/translate_abstracts.py --engine deepl --only-calibration

    # 全件
    python -X utf8 scripts/translate_abstracts.py --engine deepl

出力: screening/abstract_ja.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
csv.field_size_limit(10 ** 9)

from api_search_common import load_dotenv as load_env  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCREENING = ROOT / "screening"
CACHE = SCREENING / "abstract_ja.json"

# DeepL 無料枠。超過分は課金されるので、既定では確認を挟む。
FREE_TIER_CHARS = 500_000
DEEPL_BATCH = 40          # 1リクエストあたりのテキスト数（API上限は50）


def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def load_cache() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict) -> None:
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1, sort_keys=True),
                     encoding="utf-8")


def load_records(sheet_id: str) -> list[dict]:
    path = SCREENING / f"sheet_{sheet_id}.csv"
    if not path.exists():
        sys.exit(f"[ERROR] {path} が無い")
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("record_id")]
    # 校正セットの正は assignment.csv（sheet_*.csv は生成時点のスナップショット）
    apath = SCREENING / "assignment.csv"
    if apath.exists():
        with apath.open(encoding="utf-8-sig", newline="") as f:
            cal = {r["record_id"]: r.get("calibration", "N")
                   for r in csv.DictReader(f) if r.get("record_id")}
        for r in rows:
            r["calibration"] = cal.get(r["record_id"], r.get("calibration", "N"))
    return rows


# --- バックエンド ------------------------------------------------------------
# 追加するときは translate(texts) -> list[str] と name/model を持つ関数を足す。

def deepl_translate(texts: list[str]) -> list[str]:
    import requests
    key = os.environ.get("DEEPL_API_KEY", "").strip()
    if not key:
        sys.exit("[ERROR] DEEPL_API_KEY が未設定。.env に足すこと（.env はコミットしない）。\n"
                 "        無料版のキーは末尾が ':fx'。")
    url = ("https://api-free.deepl.com/v2/translate" if key.endswith(":fx")
           else "https://api.deepl.com/v2/translate")
    data = [("target_lang", "JA"), ("source_lang", "EN"),
            ("split_sentences", "1"), ("preserve_formatting", "1")]
    data += [("text", t) for t in texts]
    for attempt in range(5):
        r = requests.post(url, data=data, headers={"Authorization": f"DeepL-Auth-Key {key}"},
                          timeout=120)
        if r.status_code == 429 or r.status_code >= 500:
            wait = 2 ** attempt
            print(f"    [retry] HTTP {r.status_code} — {wait}s 待機")
            time.sleep(wait)
            continue
        if r.status_code == 456:
            sys.exit("[ERROR] DeepL の文字数上限に達した（HTTP 456）。"
                     "翌月まで待つか、--only-calibration で範囲を絞ること。")
        r.raise_for_status()
        return [t["text"] for t in r.json()["translations"]]
    sys.exit("[ERROR] DeepL へのリクエストが繰り返し失敗した")


ENGINES = {"deepl": {"fn": deepl_translate, "model": "deepl-api-v2"}}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", default="author")
    ap.add_argument("--engine", choices=sorted(ENGINES), help="省略時は見積もりのみ")
    ap.add_argument("--only-calibration", action="store_true",
                    help="校正セットだけ翻訳する（無料枠に収まりやすい）")
    ap.add_argument("--limit", type=int, help="翻訳する件数の上限")
    ap.add_argument("--estimate", action="store_true", help="文字数を数えるだけ（通信しない）")
    ap.add_argument("--yes", action="store_true", help="確認プロンプトを出さない")
    args = ap.parse_args()

    load_env()
    rows = load_records(args.id)
    cache = load_cache()

    todo = []
    for r in rows:
        ab = (r.get("abstract") or "").strip()
        if not ab:
            continue
        if args.only_calibration and r.get("calibration") != "Y":
            continue
        got = cache.get(r["record_id"])
        if got and got.get("src_sha1") == sha1(ab):
            continue                       # 既訳・原文も変わっていない
        todo.append((r["record_id"], ab))

    if args.limit:
        todo = todo[:args.limit]

    chars = sum(len(t) for _, t in todo)
    scope = "校正セット" if args.only_calibration else "全件"
    print(f"[INFO] 対象 {scope}: 未翻訳 {len(todo):,} 件 / {chars:,} 字"
          f"（キャッシュ済み {len(cache):,} 件）")
    if chars:
        print(f"       DeepL 無料枠 {FREE_TIER_CHARS:,}字 の {chars / FREE_TIER_CHARS:.2f} 倍")

    if args.estimate or not args.engine:
        if not args.engine:
            print("[INFO] --engine を指定すると実際に翻訳する（見積もりのみで終了）")
        return
    if not todo:
        print("[OK] 翻訳するものは無い。")
        return

    if chars > FREE_TIER_CHARS and not args.yes:
        print(f"\n[!] 無料枠を超える（{chars:,}字）。超過分は課金されうる。")
        try:
            if input("    続行する? [y/N] ").strip().lower() not in ("y", "yes"):
                print("    中止した。--only-calibration や --limit で範囲を絞れる。")
                return
        except EOFError:
            sys.exit("    非対話環境。続行するなら --yes を付けること。")

    eng = ENGINES[args.engine]
    done = 0
    try:
        for i in range(0, len(todo), DEEPL_BATCH):
            batch = todo[i:i + DEEPL_BATCH]
            out = eng["fn"]([t for _, t in batch])
            if len(out) != len(batch):
                sys.exit(f"[ERROR] 応答数が合わない（要求 {len(batch)} / 応答 {len(out)}）")
            for (rid, src), ja in zip(batch, out):
                cache[rid] = {"ja": ja, "engine": args.engine, "model": eng["model"],
                              "src_sha1": sha1(src), "chars": len(src),
                              "date": date.today().isoformat()}
            done += len(batch)
            save_cache(cache)              # 途中で落ちても失わない
            print(f"    {done:,}/{len(todo):,} 件")
    except KeyboardInterrupt:
        save_cache(cache)
        sys.exit(f"\n[中断] ここまでの {done:,} 件はキャッシュに保存済み。再実行で続きから。")

    save_cache(cache)
    print(f"[OK] {CACHE}  （計 {len(cache):,} 件）")
    print("     閲覧アプリへ反映:")
    print(f"     python -X utf8 scripts/make_review_app.py --id {args.id} "
          f"--translations screening/abstract_ja.json")


if __name__ == "__main__":
    main()
