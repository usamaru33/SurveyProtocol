#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_screening_xlsx.py — Phase 3b 判定シートの Excel 版を生成する
================================================================================

【何を】
`make_screening_sheets.py` が作った CSV 判定シートから、評価者が実際に作業しやすい
`.xlsx` を生成する。CSV は機械可読の正、xlsx は**人が記入するための作業ファイル**。

【なぜ xlsx にするか】
1,700件以上を CSV エディタで読み書きするのは現実的でない。Excel なら
  - decision 列を**ドロップダウン**にでき、表記ゆれ(include/INCLUDE/Inc)が発生しない
  - 要旨を折り返して読める
  - 見出し固定・フィルタで「未記入だけ表示」などができる
  - メタ列をロックして誤編集を防げる
判定の質と、後段の集計の安全性がそのまま上がる。

【アクセシビリティで気をつけたこと】
- **色だけに意味を持たせない**。要旨欠落は塗り分けだけでなく `has_abstract` 列の
  "N" という文字でも判別でき、オートフィルタでも絞り込める
- 前景色と背景色のコントラストを確保し、淡い塗りに濃い文字を組み合わせる
- 既定フォントサイズを 11pt、本文列は折り返し + 上揃えで行を読みやすく
- 見出し行を固定(freeze panes)し、スクロールしても列の意味を見失わない
- 記入列だけロックを外し、**Tab キーで decision → reason → note と移動できる**
- セル結合を使わない(スクリーンリーダーと並べ替えの両方で問題になるため)
- 列見出しに日本語の説明を入れ、別紙を見なくても意味が分かるようにする

【入出力】
  入力: screening/sheet_<id>.csv(+ 記入済みがあればその内容を引き継ぐ)
  出力: screening/sheet_<id>.xlsx

実行:
  python -X utf8 scripts/make_screening_xlsx.py
  python -X utf8 scripts/make_screening_xlsx.py --only author
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(_HERE))

csv.field_size_limit(10 ** 9)

try:
    from openpyxl import Workbook
    from openpyxl.comments import Comment
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:
    sys.exit("[ERROR] openpyxl が必要です:  pip install openpyxl")

from make_screening_sheets import REVIEWERS  # noqa: E402

# --- 配色 -------------------------------------------------------------------
# 淡い背景 × 濃い文字でコントラストを確保する。色は補助であり、
# 同じ情報が必ず文字(列の値)でも取れるようにしてある。
C_HEADER_BG = "1F3864"   # 濃紺
C_HEADER_FG = "FFFFFF"
C_INPUT_BG = "FFF7E6"    # 記入列(淡い橙)
C_NOABS_BG = "FDE7E9"    # 要旨欠落行(淡い赤)
C_BORDER = "BFBFBF"
C_NOTE = "44546A"

# 列定義: (CSV列名, 表示名, 幅, 折り返すか, 記入列か)
COLUMNS = [
    ("record_id",    "ID",              13, False, False),
    ("decision",     "判定 ★",          13, False, True),
    ("reason",       "除外理由 ★",      26, True,  True),
    ("note",         "メモ",            22, True,  True),
    ("title",        "タイトル",         52, True,  False),
    ("abstract",     "要旨",             95, True,  False),
    ("venue",        "掲載先",           30, True,  False),
    ("year",         "年",                7, False, False),
    ("rank",         "ランク",           11, False, False),
    ("has_abstract", "要旨有無",          9, False, False),
    ("kw_groups",    "概念群",            8, False, False),
    ("doi",          "DOI",              26, False, False),
    ("block",        "ブロック",          9, False, False),
]

HEADER_HELP = {
    "判定 ★": "この列を埋めてください。セルを選ぶとドロップダウンが出ます。\n"
              "Include=残す / Exclude=除外 / Unsure=判断保留(協議に回ります)",
    "除外理由 ★": "Exclude のときは必須です。抵触した PICOS 基準を書いてください。\n"
                  "例) P: 患者対象 / I: HMDでない / S: ユーザー実験なし",
    "メモ": "任意。協議で持ち出したい論点があれば。",
    "要旨有無": "N = 要旨が無く、タイトルだけで判断することになる文献です。",
    "概念群": "検索クエリの3概念群がいくつ当たったか(0〜3)。\n"
              "**読む順序の目安にすぎません。この値で判定しないでください。**",
    "ランク": "Phase 2 で既に基準を満たしています。判定材料にはしないでください。",
}

DECISIONS = ["Include", "Exclude", "Unsure"]

INTRO = [
    ("Phase 3b  Title/Abstract スクリーニング  判定シート", "title"),
    ("", ""),
    ("担当: {reviewer}", "lead"),
    ("担当件数: {n:,} 件", "lead"),
    ("", ""),
    ("■ やること", "h"),
    ("「判定」シートの ★ が付いた2列を埋めてください。", ""),
    ("  ・判定 … Include(残す) / Exclude(除外) / Unsure(保留) から選ぶ", ""),
    ("  ・除外理由 … Exclude のときは必須。抵触した PICOS 基準を書く", ""),
    ("", ""),
    ("■ 判定の考え方", "h"),
    ("除外できると確信できないものは残してください(Include)。", ""),
    ("全文を読めば分かることを、この段階で切らないためです。", ""),
    ("迷ったら Unsure で構いません。Unsure は後で協議にかけます。", ""),
    ("", ""),
    ("■ お願い", "h"),
    ("他の評価者のファイルは開かないでください。", "warn"),
    ("二重スクリーニングは互いの判定を見ないことが前提で、", ""),
    ("見てしまうと評価者間一致度(κ)が意味を失います。", ""),
    ("", ""),
    ("■ 使い方のヒント", "h"),
    ("・見出し行は固定してあります。横スクロールしても列名が残ります。", ""),
    ("・オートフィルタで「判定」を (空白) で絞ると未記入だけ表示できます。", ""),
    ("・薄い赤の行は要旨が無い文献です(「要旨有無」列が N)。", ""),
    ("  タイトルだけで判断することになるので、無理なら Unsure にしてください。", ""),
    ("・「概念群」は読む順序の目安です。並べ替えの基準に使ってあるだけで、", ""),
    ("  この数値で判定しないでください。", ""),
    ("・入力する3列以外はロックしてあります(誤編集の防止)。", ""),
    ("", ""),
    ("■ 要旨を全文読むには", "h"),
    ("要旨は平均1,300字ほどあり、セルには冒頭の5行程度しか表示されません。", ""),
    ("全文を読むときは次のどちらかで開いてください。", ""),
    ("  (1) その行の行番号を右クリック →「行の高さの自動調整」", "lead"),
    ("      読み終わったら元に戻せます。行の高さ変更は許可してあります。", ""),
    ("  (2) 要旨のセルを選び、数式バー右端の∨ボタンで数式バーを広げる", "lead"),
    ("行を全部広げると走査しづらくなるので、既定は詰めた高さにしてあります。", ""),
    ("", ""),
    ("■ 終わったら", "h"),
    ("このファイルを著者に渡してください。集計とκの算出はスクリプトが行います。", ""),
]


def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        return list(csv.DictReader(f))


def build_intro(ws, reviewer: str, n: int) -> None:
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 92
    styles = {
        "title": Font(size=16, bold=True, color=C_HEADER_BG),
        "h":     Font(size=12, bold=True, color=C_HEADER_BG),
        "lead":  Font(size=11, bold=True),
        "warn":  Font(size=11, bold=True, color="9C0006"),
        "":      Font(size=11),
    }
    for i, (text, kind) in enumerate(INTRO, start=1):
        c = ws.cell(row=i, column=1,
                    value=text.format(reviewer=reviewer, n=n) if text else "")
        c.font = styles[kind]
        c.alignment = Alignment(vertical="center", wrap_text=False)
        ws.row_dimensions[i].height = 24 if kind in ("title", "h") else 18
    ws.protection.sheet = True   # 説明シートは編集不可


def build_sheet(ws, rows: list[dict]) -> None:
    thin = Side(style="thin", color=C_BORDER)
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # --- 見出し ---
    for j, (_key, label, width, _wrap, _inp) in enumerate(COLUMNS, start=1):
        c = ws.cell(row=1, column=j, value=label)
        c.font = Font(bold=True, color=C_HEADER_FG, size=11)
        c.fill = PatternFill("solid", fgColor=C_HEADER_BG)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = border
        ws.column_dimensions[get_column_letter(j)].width = width
        if label in HEADER_HELP:
            c.comment = Comment(HEADER_HELP[label], "screening protocol")
            c.comment.width = 320
            c.comment.height = 110
    ws.row_dimensions[1].height = 32

    # --- 本体 ---
    input_fill = PatternFill("solid", fgColor=C_INPUT_BG)
    for i, row in enumerate(rows, start=2):
        for j, (key, _label, _w, wrap, is_input) in enumerate(COLUMNS, start=1):
            val = row.get(key, "")
            if key in ("year", "kw_groups", "block"):
                try:
                    val = int(val)
                except (TypeError, ValueError):
                    pass
            c = ws.cell(row=i, column=j, value=val)
            c.alignment = Alignment(
                vertical="top", wrap_text=wrap,
                horizontal="center" if key in ("year", "kw_groups", "block",
                                               "has_abstract", "decision") else "left")
            c.border = border
            c.font = Font(size=11)
            if is_input:
                c.fill = input_fill
                c.protection = Protection(locked=False)
            else:
                c.protection = Protection(locked=True)
        # 要旨は中央値 1,278 文字あり、セルに全文を収めると1行が15行分の高さになって
        # 走査できなくなる。ここでは「タイトル全文 + 要旨の冒頭5行」が見える高さに抑え、
        # 全文を読む手順を「はじめに」シートに明示する(行の書式変更は保護から除外済み)。
        ws.row_dimensions[i].height = 85

    last = len(rows) + 1
    ws.freeze_panes = "B2"                     # 見出し行 + ID 列を固定
    ws.auto_filter.ref = f"A1:{get_column_letter(len(COLUMNS))}{last}"

    # --- 判定列のドロップダウン ---
    dcol = get_column_letter(1 + [c[0] for c in COLUMNS].index("decision"))
    dv = DataValidation(type="list", formula1='"' + ",".join(DECISIONS) + '"',
                        allow_blank=True, showDropDown=False)
    dv.error = "Include / Exclude / Unsure のいずれかを選んでください。"
    dv.errorTitle = "入力できない値です"
    dv.prompt = "Include=残す / Exclude=除外 / Unsure=保留"
    dv.promptTitle = "判定"
    ws.add_data_validation(dv)
    dv.add(f"{dcol}2:{dcol}{last}")

    # --- 条件付き書式 -------------------------------------------------------
    # (1) 要旨が無い行を淡く塗る。※色は補助で、「要旨有無」列の N でも判別できる
    hcol = get_column_letter(1 + [c[0] for c in COLUMNS].index("has_abstract"))
    ws.conditional_formatting.add(
        f"A2:{get_column_letter(len(COLUMNS))}{last}",
        FormulaRule(formula=[f'${hcol}2="N"'],
                    fill=PatternFill("solid", fgColor=C_NOABS_BG), stopIfTrue=False))
    # (2) Exclude なのに理由が空のセルを目立たせる(提出前の自己チェック用)
    rcol = get_column_letter(1 + [c[0] for c in COLUMNS].index("reason"))
    ws.conditional_formatting.add(
        f"{rcol}2:{rcol}{last}",
        FormulaRule(formula=[f'AND(${dcol}2="Exclude",LEN(TRIM(${rcol}2))=0)'],
                    fill=PatternFill("solid", fgColor="FFC7CE"),
                    font=Font(color="9C0006", bold=True), stopIfTrue=False))

    # 記入列以外をロック(パスワードなし。誤操作の防止が目的で秘匿ではない)
    ws.protection.sheet = True
    ws.protection.autoFilter = False
    ws.protection.sort = False
    ws.protection.formatColumns = False
    ws.protection.formatRows = False


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 3b 判定シートの Excel 版を生成")
    ap.add_argument("--dir", type=Path, default=ROOT / "screening")
    ap.add_argument("--only", type=str, default="",
                    help="特定の評価者だけ生成(author / kataoka / watanabe)")
    ap.add_argument("--force", action="store_true",
                    help="既存の .xlsx を上書きする(記入済みの内容は失われる)")
    args = ap.parse_args()

    targets = [args.only] if args.only else list(REVIEWERS)
    for rev in targets:
        if rev not in REVIEWERS:
            sys.exit(f"[ERROR] 未知の評価者: {rev}(有効: {', '.join(REVIEWERS)})")
        src = args.dir / f"sheet_{rev}.csv"
        dst = args.dir / f"sheet_{rev}.xlsx"
        if not src.exists():
            print(f"[SKIP] {src.name} が無い。先に make_screening_sheets.py を実行すること")
            continue
        if dst.exists() and not args.force:
            print(f"[SKIP] {dst.name} は既にある(記入済みを壊さないため生成しない。"
                  f"作り直すなら --force)")
            continue

        rows = load_rows(src)
        wb = Workbook()
        intro = wb.active
        intro.title = "はじめに"
        build_intro(intro, REVIEWERS[rev], len(rows))
        ws = wb.create_sheet("判定")
        build_sheet(ws, rows)
        wb.active = 1          # 開いたとき「判定」シートを表示
        wb.save(dst)

        no_abs = sum(1 for r in rows if r.get("has_abstract") == "N")
        print(f"[INFO] 出力: {dst.name}  {len(rows):,} 行  担当={REVIEWERS[rev]}"
              f"  (うち要旨なし {no_abs} 件)")

    print("\n[NEXT] 各評価者に .xlsx を配布する。記入後は screening/ に戻してもらい、")
    print("       `python -X utf8 scripts/score_screening.py` で集計する")
    print("       (xlsx があれば xlsx を、無ければ CSV を読む)。")


if __name__ == "__main__":
    main()
