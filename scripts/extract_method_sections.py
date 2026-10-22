#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""抽出本文(fulltext/txt)から、手法・実験にかかわる節(Method 等)だけを切り出す。

  python -X utf8 scripts/extract_method_sections.py            # 全件。fulltext/method/<id>.json を書き、集計を表示
  python -X utf8 scripts/extract_method_sections.py --id R027918b25   # 1 本だけ内容を表示

節は「手法系の見出し」から「結果・考察系の見出し」の手前まで。複数の実験がある論文は複数の節を拾う。
見出しが取れない論文は sections が空になる(その旨をアプリに出す)。AI を使わず、見出しの文字列だけで切る。
出力は著作物の派生物なので .gitignore 対象。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TXT = ROOT / "fulltext" / "txt"
OUT = ROOT / "fulltext" / "method"

NUM = r"(?:(?:\d+(?:\.\d+)*|[IVX]+)\.?\s+)?"
EXP = r"(?:(?:experiment|study|exp\.?)\s*\d+\s*[:.\-–—]?\s*)?"
START_WORDS = (
    r"methods?|methodology|materials?(?:\s+and\s+methods?)?|methods?\s+and\s+materials?|"
    r"experiment(?:al)?(?:\s+(?:design|setup|set-up|procedure|method|methods))?|"
    r"study(?:\s+design)?|procedure|participants?|subjects?|apparatus|stimuli|"
    r"design(?:\s+and\s+procedure)?|experimental\s+(?:design|setup|set-up|procedure)|"
    r"user\s+study|evaluation|measures?|measurements?"
)
END_WORDS = (
    r"results?(?:\s+and\s+discussion)?|findings|discussion|general\s+discussion|conclusions?|"
    r"limitations?|references|bibliography|acknowledg(?:e)?ments?|appendix"
)
RE_START = re.compile(rf"^{NUM}{EXP}(?:{START_WORDS})(?:\s*[:\-–—]\s*\w.*)?$", re.I)
RE_END = re.compile(rf"^{NUM}{EXP}(?:{END_WORDS})(?:\s*[:\-–—]\s*\w.*)?$", re.I)
RE_STOP = re.compile(rf"^{NUM}(?:references|bibliography)$", re.I)
RE_PAGE = re.compile(r"^\[p\.(\d+)\]\s*$")
# 「Study 1」「Experiment 2」だけの見出しも、手法の開始として扱う
RE_EXPONLY = re.compile(r"^(?:experiment|study|exp\.?)\s*\d+\s*(?:[:.\-–—].{0,60})?$", re.I)

# 「Background and Methodology」のように Method を含む短い見出し
RE_METHODHEAD = re.compile(r"^(?:[A-Z][A-Za-z]*\s+){0,3}(?:and\s+)?methods?(?:ology)?$|^.{0,30}methodology$", re.I)

MAX_HEAD = 70


def head_kind(line: str) -> str | None:
    s = line.strip()
    if not s or len(s) > MAX_HEAD or s.endswith((",", ";")):
        return None
    s = re.sub(r"\s+", " ", s)
    if not (s[0].isupper() or s[0].isdigit()):   # 折り返した本文の行を見出しと誤認しない
        return None
    if RE_STOP.match(s):      # 参考文献は節の終わり。Science 系は Methods が参考文献の後ろにあるので読み続ける
        return "end"
    if RE_END.match(s):
        return "end"
    if RE_START.match(s) or RE_EXPONLY.match(s) or RE_METHODHEAD.match(s):
        return "start"
    return None


def extract(text: str) -> dict:
    lines = text.splitlines()
    page = 1
    secs: list[dict] = []
    cur: dict | None = None
    seen_start = False
    for ln in lines:
        m = RE_PAGE.match(ln.strip())
        if m:
            page = int(m.group(1))
            if cur is not None:
                cur["lines"].append(f"[p.{page}]")
            continue
        k = head_kind(ln)
        if k == "start":
            seen_start = True
            if cur is None:
                cur = {"heading": ln.strip(), "page": page, "lines": []}
                continue
        elif k == "end" and cur is not None:
            secs.append(cur)
            cur = None
            continue
        if cur is not None:
            cur["lines"].append(ln)
    if cur is not None and cur["lines"]:
        secs.append(cur)
    out = []
    for s in secs:
        body = "\n".join(s["lines"]).strip()
        if len(body) < 200:        # 見出しだけ・目次の拾い誤りを除く
            continue
        out.append({"heading": s["heading"], "page": s["page"], "text": body})
    return {"sections": out, "chars": sum(len(x["text"]) for x in out)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    files = [TXT / f"{a.id}.txt"] if a.id else sorted(TXT.glob("*.txt"))
    none, rows = [], []
    for f in files:
        rid = f.stem
        txt = f.read_text(encoding="utf-8")
        r = extract(txt)
        r["id"] = rid
        r["total_chars"] = len(txt)
        if a.id:
            for s in r["sections"]:
                print(f"=== {s['heading']} (p.{s['page']}) {len(s['text'])}字")
                print(s["text"][:600], "\n...")
            print(f"節 {len(r['sections'])} / {r['chars']}字 / 全文 {len(txt)}字")
            return 0
        (OUT / f"{rid}.json").write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
        rows.append((rid, len(r["sections"]), r["chars"], len(txt)))
        if not r["sections"]:
            none.append(rid)
    n = len(rows)
    tot = sum(x[3] for x in rows)
    got = sum(x[2] for x in rows)
    print(f"{n} 本中、節が取れた {n - len(none)} 本 / 取れない {len(none)} 本")
    print(f"抽出 {got:,} 字 / 全文 {tot:,} 字({got / tot:.0%})")
    small = [x for x in rows if x[1] and x[2] < 3000]
    big = [x for x in rows if x[3] and x[2] / x[3] > 0.6]
    print(f"3,000 字未満(少なすぎ疑い): {len(small)} 本 / 全文の 6 割超(多すぎ疑い): {len(big)} 本")
    if none:
        print("取れない:", " ".join(none))
    return 0


if __name__ == "__main__":
    sys.exit(main())
