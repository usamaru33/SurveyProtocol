"""ブラウザで手動取得した全文 PDF を、中身で論文を照合して record_id に振り分ける。

使い方:
    python -X utf8 scripts/sort_fulltext_inbox.py                 # fulltext/inbox/ を処理
    python -X utf8 scripts/sort_fulltext_inbox.py --inbox ~/Downloads --dry-run
    python -X utf8 scripts/sort_fulltext_inbox.py --assign "foo.pdf=R12624d2c7"   # 照合できない分を手で指定

入力  : 受け箱フォルダの *.pdf(ファイル名は何でもよい)と fulltext/manifest.csv
出力  : fulltext/pdf/<record_id>.pdf(受け箱から移動)・担当ペアへのコピー・manifest.csv の更新・
        manual_fetch.md の再生成

照合は1〜2ページ目の本文で行う:
  1. manifest のタイトル(正規化)が本文にそのまま含まれる
  2. 含まれなければ、タイトルの語の 90% 以上が本文に現れ、かつ候補が1件に絞れる
  3. 1ページ目に記録の DOI が現れる(参考文献の DOI と混同しないよう1ページ目だけを見る)
候補が0件・複数件のファイルは割り当てず受け箱に残す(取り違えるより人が確認する方が安い)。
missing の記録だけを照合対象にし、取得済み PDF は上書きしない。
"""
import argparse
import csv
import re
import shutil
from pathlib import Path

import fitz  # PyMuPDF

from fetch_fulltext import ROOT, write_manual_list

OUT = ROOT / "fulltext"


def norm(t: str) -> str:
    return re.sub(r"[^0-9a-z]+", " ", t.lower()).strip()


def page_texts(pdf: Path) -> tuple[str, str]:
    """(1ページ目, 1〜2ページ目) の正規化テキスト。ハイフン改行はつなげる。"""
    with fitz.open(pdf) as d:
        pages = [d[i].get_text() for i in range(min(2, len(d)))]
    pages = [re.sub(r"-\n(?=[a-z])", "", p) for p in pages]
    return pages[0] if pages else "", " ".join(pages)


def match(pdf: Path, records: list[dict]) -> tuple[list[dict], str]:
    raw1, raw12 = page_texts(pdf)
    text = f" {norm(raw12)} "
    words = set(text.split())
    exact = [r for r in records if len(norm(r["title"])) >= 20 and f" {norm(r['title'])} " in text]
    if exact:
        return exact, "タイトル一致"
    # 語の一致は「タイトル長+5語の窓の中に集中して現れる」ことを要求する。本文全体の語の集合で
    # 判定すると、分野の頻出語(virtual, perception, size …)だけで無関係な論文に当たってしまう
    tokens = text.split()
    fuzzy = []
    for r in records:
        tw = norm(r["title"]).split()
        if len(tw) < 5 or sum(w in words for w in tw) / len(tw) < 0.9:
            continue
        span = len(tw) + 5
        need = set(tw)
        if any(len(need & set(tokens[i:i + span])) / len(need) >= 0.9
               for i in range(max(1, len(tokens) - span + 1))):
            fuzzy.append(r)
    if fuzzy:
        return fuzzy, "タイトル語の一致"
    p1 = raw1.lower()
    by_doi = [r for r in records if r["doi"] and r["doi"].lower() in p1]
    return by_doi, "1ページ目の DOI"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", type=Path, default=OUT / "inbox")
    ap.add_argument("--assign", action="append", default=[],
                    help="照合できないファイルを手で割り当てる: ファイル名=record_id(複数可)")
    ap.add_argument("--dry-run", action="store_true", help="照合結果だけ表示し、何も動かさない")
    args = ap.parse_args()

    mpath = OUT / "manifest.csv"
    rows = list(csv.DictReader(mpath.open(encoding="utf-8-sig", newline="")))
    by_id = {r["record_id"]: r for r in rows}
    forced = dict(a.split("=", 1) for a in args.assign)
    for name, rid in forced.items():
        if rid not in by_id:
            raise SystemExit(f"--assign の record_id が manifest に無い: {rid}")

    pdfs = sorted(p for p in args.inbox.glob("*") if p.suffix.lower() == ".pdf")
    if not pdfs:
        print(f"受け箱に PDF がありません: {args.inbox}")
        return

    taken, left = [], []
    for pdf in pdfs:
        if pdf.read_bytes()[:5] != b"%PDF-":
            left.append((pdf.name, "PDF ではない(ログイン画面などを保存した可能性)"))
            continue
        missing = [r for r in rows if r["status"] != "ok" and r["record_id"] not in {t[1] for t in taken}]
        if pdf.name in forced:
            cands, how = [by_id[forced[pdf.name]]], "手動指定"
        else:
            try:
                cands, how = match(pdf, missing)
            except Exception as e:
                left.append((pdf.name, f"読み取り失敗: {type(e).__name__}"))
                continue
        if len(cands) != 1:
            why = "該当なし" if not cands else "候補が複数: " + ", ".join(r["record_id"] for r in cands)
            left.append((pdf.name, why))
            continue
        r = cands[0]
        if r["status"] == "ok":
            left.append((pdf.name, f"{r['record_id']} は取得済み(上書きしない)"))
            continue
        taken.append((pdf.name, r["record_id"], how))
        if args.dry_run:
            continue
        dest = OUT / "pdf" / f"{r['record_id']}.pdf"
        shutil.move(str(pdf), dest)
        for who in r["pair"].split("×"):
            d = OUT / "by_reviewer" / who
            d.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(dest, d / dest.name)
        r["status"], r["source"] = "ok", f"manual: {pdf.name}"

    for name, rid, how in taken:
        print(f"  OK  {name} → {rid}({how}) {by_id[rid]['title'][:60]}")
    for name, why in left:
        print(f"  --  {name}: {why}")

    if not args.dry_run and taken:
        with mpath.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        write_manual_list(rows, OUT / "manual_fetch.md")
    ok = sum(r["status"] == "ok" for r in rows)
    print(f"割り当て {len(taken)} 件 / 残り {len(left)} 件(受け箱に残置)。"
          f"取得済み {ok} / {len(rows)} 件{'(dry-run: 何も変更していない)' if args.dry_run else ''}")


if __name__ == "__main__":
    main()
