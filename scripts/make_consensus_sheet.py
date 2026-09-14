#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_consensus_sheet.py — 協議ミーティング用シートの生成
================================================================================

【何を】
`consensus_worklist.csv`(不一致・Unsure)の各レコードについて、著者・Kataoka・
Watanabe **3名全員の判定・除外理由・メモ**を1行に並べたシートを作る。

判定中は他人のシートを見ない(独立性)が原則だが、この段階は逆で
**3名が互いの判定を見ながら1つの結論に決める**協議そのものが目的なので、
全員分を並べて出す。校正セット(3名全員が判定済み)のみが対象。

書式は評価者に配布した個人シート(`make_screening_xlsx.py`)にできるだけ揃えた
(見出し配色・枠線・保護・「はじめに」シート・列見出しのコメント)。異なるのは、
1列1名分だった判定/理由/メモが3名分横並びになる点と、個人シートには無い
「内訳」(何対何で割れているか)列を追加した点。

【入出力】
  入力: screening/assignment.csv, screening/sheet_<id>.csv, screening/supplement_sheet_<id>.csv
        (xlsx があれば xlsx を優先。score_screening.py と同じ読み込みを使う)
  出力: screening/consensus_meeting.xlsx

実行:
  python -X utf8 scripts/make_consensus_sheet.py
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
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

from make_screening_sheets import REVIEWERS as _  # noqa: E402  (存在確認のみ)
from score_screening import VALID, CANON, load_sheet  # noqa: E402

# --- 配色(個人シートと同一) ---------------------------------------------------
C_HEADER_BG = "1F3864"
C_HEADER_FG = "FFFFFF"
C_INPUT_BG = "FFF7E6"
C_FLAG_BG = "FDE7E9"     # 3者バラバラの行(個人シートの「要旨欠落」行と同系色)
C_BORDER = "BFBFBF"

FINAL_CHOICES = ["Include", "Exclude", "Unsure"]
REVIEWER_ORDER = ["author", "kataoka", "watanabe"]
REVIEWER_LABEL = {"author": "著者", "kataoka": "Kataoka", "watanabe": "Watanabe"}

# 列定義: (表示名, 幅, 折り返すか, 記入列か)
# 幅は make_screening_xlsx.COLUMNS の対応列(ID/タイトル/DOI/掲載先/要旨/判定/理由/メモ)に合わせた。
META_COLUMNS = [
    ("ID", 13, False, False),
    ("タイトル", 52, True, False),
    ("DOI", 26, False, False),
    ("掲載先", 30, True, False),
    ("要旨", 95, True, False),
]
PER_REVIEWER_COLUMNS = [
    ("判定", 13, False, False),
    ("理由", 34, True, False),
    ("メモ", 22, True, False),
]
TAIL_COLUMNS = [
    ("内訳", 20, False, False),
    ("最終判定 ★", 13, False, True),
    ("協議メモ ★", 34, True, True),
]

HEADER_HELP = {
    "要旨": "個人シートと同じ要旨です。全文を読むには行の高さを一時的に広げてください"
            "(行番号を右クリック→「行の高さの自動調整」)。",
}
for rv in REVIEWER_ORDER:
    HEADER_HELP[f"{REVIEWER_LABEL[rv]}:判定"] = (
        "この評価者の判定です(記入済み・読み取り専用)。\n"
        "Include=残す / Exclude=除外 / Unsure=判断保留")
    HEADER_HELP[f"{REVIEWER_LABEL[rv]}:理由"] = "Exclude のときの除外理由(読み取り専用)。"
    HEADER_HELP[f"{REVIEWER_LABEL[rv]}:メモ"] = "この評価者が残したメモ(読み取り専用)。"
HEADER_HELP["内訳"] = ("3名の判定の集計です。例: Exclude×2 / Unsure×1\n"
                        "同じ値が3つ並ぶ行は淡い赤で強調しています(3者が3通りに割れている行)。")
HEADER_HELP["最終判定 ★"] = ("ミーティングで決まった最終判定を選んでください。\n"
                              "Include / Exclude / Unsure から選択式です。\n"
                              "協議で解決しない場合は Include に倒します(再現率優先、rule.md Phase 3b)。")
HEADER_HELP["協議メモ ★"] = "協議で出た論点・決定理由を記録してください。任意ですが、後から追える程度に。"

INTRO = [
    ("Phase 3b  協議ミーティング用シート", "title"),
    ("", ""),
    ("対象件数: {n:,} 件（校正セット223件のうち、不一致・Unsure）", "lead"),
    ("", ""),
    ("■ このシートについて", "h"),
    ("個人の判定シートとは異なり、著者・Kataoka・Watanabe **3名全員の判定を並べて**", ""),
    ("表示しています。ミーティングで見比べながら最終判定を1つに決めるための資料です。", ""),
    ("(通常のスクリーニングでは他人の判定を見ないことが独立性の前提ですが、", ""),
    (" この協議の段階はその逆で、全員で見比べて結論を出すことが目的です。)", ""),
    ("", ""),
    ("■ 列の意味", "h"),
    ("・著者/Kataoka/Watanabe の 判定・理由・メモ … 各評価者が個人シートに記入したもの(読み取り専用)", ""),
    ("・内訳 … 3名の判定の集計(例: Exclude×2 / Unsure×1)。3者が3通りに割れている行は", ""),
    ("  淡い赤で強調し、シート上部にまとめています(合意形成に時間がかかりやすいため)", ""),
    ("", ""),
    ("■ やること", "h"),
    ("「最終判定 ★」「協議メモ ★」の2列だけを埋めてください。どちらも下の方針に沿って記入します。", ""),
    ("  ・最終判定 … Include(残す) / Exclude(除外) / Unsure(保留) から選ぶ", ""),
    ("  ・協議メモ … 決定理由や論点を書く(任意)", ""),
    ("協議で結論が出ない場合は Include に倒してください(誤 Exclude は回復不能、誤 Include は", ""),
    ("Phase 4 の手間が増えるだけ、という非対称性のためです)。", "lead"),
    ("", ""),
    ("■ 使い方のヒント", "h"),
    ("・見出し行と ID・タイトル・DOI・掲載先の4列は固定してあります。", ""),
    ("・入力する2列以外はロックしてあります(誤編集の防止)。", ""),
    ("", ""),
    ("■ 終わったら", "h"),
    ("この内容を screening/consensus_worklist.csv の final_decision / consensus_note へ転記し、", ""),
    ("score_screening.py を再実行してください(final_decisions.csv が確定します)。", ""),
]


def load_all_sheets() -> dict[str, dict[str, dict]]:
    sheets = {}
    for rid in REVIEWER_ORDER:
        base = load_sheet(ROOT / "screening" / f"sheet_{rid}.csv")
        sup = load_sheet(ROOT / "screening" / f"supplement_sheet_{rid}.csv")
        merged = dict(sup)
        merged.update(base)
        sheets[rid] = merged
    return sheets


def vote_summary(decisions: list[str]) -> str:
    c = Counter(decisions)
    return " / ".join(f"{k}×{v}" for k, v in c.most_common())


def build_intro(ws, n: int) -> None:
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 104
    styles = {
        "title": Font(size=16, bold=True, color=C_HEADER_BG),
        "h":     Font(size=12, bold=True, color=C_HEADER_BG),
        "lead":  Font(size=11, bold=True),
        "":      Font(size=11),
    }
    for i, (text, kind) in enumerate(INTRO, start=1):
        c = ws.cell(row=i, column=1, value=text.format(n=n) if text else "")
        c.font = styles[kind]
        c.alignment = Alignment(vertical="center", wrap_text=False)
        ws.row_dimensions[i].height = 24 if kind in ("title", "h") else 18
    ws.protection.sheet = True


def build_sheet(ws, rows: list[dict]) -> None:
    thin = Side(style="thin", color=C_BORDER)
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    columns: list[tuple[str, int, bool, bool]] = list(META_COLUMNS)
    for rv in REVIEWER_ORDER:
        for label, width, wrap, is_input in PER_REVIEWER_COLUMNS:
            columns.append((f"{REVIEWER_LABEL[rv]}:{label}", width, wrap, is_input))
    columns += list(TAIL_COLUMNS)
    n_distinct_col = len(columns) + 1   # 隠し列(条件付き書式の判定用)

    # --- 見出し ---
    for j, (label, width, _wrap, _inp) in enumerate(columns, start=1):
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
        vals: list = [row["record_id"], row["title"], row["doi"], row["venue"], row["abstract"]]
        for rv in REVIEWER_ORDER:
            pr = row["per_reviewer"][rv]
            vals += [pr["decision"], pr["reason"], pr["note"]]
        vals += [row["vote"], row["final_decision"], row["consensus_note"]]

        for j, (val, (_label, _w, wrap, is_input)) in enumerate(zip(vals, columns), start=1):
            c = ws.cell(row=i, column=j, value=val)
            c.border = border
            c.font = Font(size=11)
            c.alignment = Alignment(vertical="top", wrap_text=wrap, horizontal="left")
            if is_input:
                c.fill = input_fill
                c.protection = Protection(locked=False)
            else:
                c.protection = Protection(locked=True)
        ws.cell(row=i, column=n_distinct_col, value=row["n_distinct"])
        ws.row_dimensions[i].height = 85

    last = len(rows) + 1
    ws.freeze_panes = "C2"     # 見出し行 + ID・タイトル列を固定(個人シートは ID 列のみ固定)
    ws.auto_filter.ref = f"A1:{get_column_letter(len(columns))}{last}"

    # --- 最終判定列のドロップダウン(個人シートの判定列と同じ方式) ---
    final_idx = 1 + [c[0] for c in columns].index("最終判定 ★")
    dcol = get_column_letter(final_idx)
    dv = DataValidation(type="list", formula1='"' + ",".join(FINAL_CHOICES) + '"',
                        allow_blank=True, showDropDown=False)
    dv.error = "Include / Exclude / Unsure のいずれかを選んでください。"
    dv.errorTitle = "入力できない値です"
    dv.prompt = "ミーティングで決まった最終判定。協議で解決しなければ Include に倒す(再現率優先)。"
    dv.promptTitle = "最終判定"
    ws.add_data_validation(dv)
    dv.add(f"{dcol}2:{dcol}{last}")

    # --- 3者が3通りに割れている行を強調(個人シートの「要旨欠落」行と同じ手法: 隠し列を条件式で参照) ---
    ncol = get_column_letter(n_distinct_col)
    ws.conditional_formatting.add(
        f"A2:{get_column_letter(len(columns))}{last}",
        FormulaRule(formula=[f"${ncol}2>=3"],
                    fill=PatternFill("solid", fgColor=C_FLAG_BG), stopIfTrue=False))
    ws.column_dimensions[ncol].hidden = True

    ws.protection.sheet = True
    ws.protection.autoFilter = False
    ws.protection.sort = False
    ws.protection.formatColumns = False
    ws.protection.formatRows = False


def main() -> None:
    wpath = ROOT / "screening" / "consensus_worklist.csv"
    if not wpath.exists():
        sys.exit(f"[ERROR] {wpath} がありません。先に score_screening.py を実行すること")
    with wpath.open(encoding="utf-8-sig", newline="") as f:
        worklist = list(csv.DictReader(f))

    sheets = load_all_sheets()

    rows = []
    for w in worklist:
        rid = w["record_id"]
        per_reviewer = {}
        decisions = []
        for rv in REVIEWER_ORDER:
            r = sheets[rv].get(rid, {})
            d = (r.get("decision") or "").strip().lower()
            d = CANON[d] if d in VALID else ""
            per_reviewer[rv] = {
                "decision": d,
                "reason": r.get("reason", ""),
                "note": r.get("note", ""),
            }
            if d:
                decisions.append(d)
        title = w.get("title") or next(
            (sheets[rv][rid]["title"] for rv in REVIEWER_ORDER if rid in sheets[rv]), "")
        abstract = next(
            (sheets[rv][rid].get("abstract", "") for rv in REVIEWER_ORDER if rid in sheets[rv]), "")
        venue = next(
            (sheets[rv][rid].get("venue", "") for rv in REVIEWER_ORDER if rid in sheets[rv]), "")
        rows.append({
            "record_id": rid,
            "title": title,
            "doi": w.get("doi", ""),
            "venue": venue,
            "abstract": abstract,
            "per_reviewer": per_reviewer,
            "vote": vote_summary(decisions),
            "n_distinct": len(set(decisions)),
            "final_decision": (w.get("final_decision") or "").strip(),
            "consensus_note": (w.get("consensus_note") or "").strip(),
        })

    # 3者が3通りに割れているものを先頭へ(合意形成が最も難しい順)
    rows.sort(key=lambda r: (-r["n_distinct"], r["record_id"]))

    wb = Workbook()
    intro = wb.active
    intro.title = "はじめに"
    n_flagged = sum(1 for r in rows if r["n_distinct"] >= 3)
    build_intro(intro, len(rows))
    ws = wb.create_sheet("協議")
    build_sheet(ws, rows)
    wb.active = 1
    wb.save(ROOT / "screening" / "consensus_meeting.xlsx")

    print(f"[INFO] 出力: screening/consensus_meeting.xlsx  ({len(rows):,} 件)")
    print(f"       3者が3通りに割れているもの: {n_flagged} 件(先頭に配置・淡い赤でハイライト)")
    print("[NEXT] ミーティングで「最終判定 ★」「協議メモ ★」を記入したら、")
    print("       その内容を screening/consensus_worklist.csv の final_decision / consensus_note へ")
    print("       転記して score_screening.py を再実行すること(final_decisions.csv が生成される)。")


if __name__ == "__main__":
    main()
