#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_stage2_note.py — stage 2 シートに「境界例メモ(参考)」シートを追加する
================================================================================

【何を】
Rev.27（`docs/log/protocol_changelog.md`）で決めた対応:
著者が「I: スケール操作/多感覚刺激が無い」で Exclude とした記録には、校正セットの協議で
実際にどう判断したかを補足として添える。**新しい基準は導入しない**(Rev.19の凍結維持)。
既存の判定シート(`make_screening_xlsx.py`)には手を入れず、追加シートとして挿入するだけ。

【入出力】
  入力: screening/consensus/consensus_worklist.csv(final_decision 記入済み)
  出力: screening/stage2/stage2_sheet_<id>.xlsx に「境界例メモ(参考)」シートを追加(上書き)

実行:
  python -X utf8 scripts/add_stage2_note.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent

try:
    from openpyxl import load_workbook
    from openpyxl.styles import Alignment, Font, PatternFill
except ImportError:
    sys.exit("[ERROR] openpyxl が必要です:  pip install openpyxl")

TARGET_REASON = "I: スケール操作/多感覚刺激が無い"

INTRO_LINES = [
    ("境界例メモ(参考) — 校正セット協議での判断例", "title"),
    ("", ""),
    ("基準・除外理由の語彙は変更していません(判定シートは配布時のまま)。", "lead"),
    ("以下は校正セット223件の協議で「I: スケール操作/多感覚刺激が無い」が絡んだ", ""),
    ("境界例について、実際にどう判断したかの記録です。参考にしてください。", ""),
    ("", ""),
    ("■ 判断の傾向", "h"),
    ("触覚刺激や身体所有感の操作があっても、測定している指標が「対人距離・感情・", ""),
    ("presence・所有感の強さ」だけで、O基準(主観的サイズ推定・距離知覚・アフォーダンス・", ""),
    ("身体所有感・客観的運動出力)の「スケール変容」に紐づいていない場合は Exclude と", ""),
    ("判断しました。身体サイズや空間スケールに明確に紐づく操作・指標がある場合は", ""),
    ("Include です。判断に迷ったら、この表と同じように Unsure にしてください。", "lead"),
    ("", ""),
]


def load_examples() -> list[dict]:
    wpath = ROOT / "screening" / "consensus" / "consensus_worklist.csv"
    with wpath.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return [r for r in rows
            if r["reason_a"].strip() == TARGET_REASON or r["reason_b"].strip() == TARGET_REASON]


def add_sheet(path: Path, examples: list[dict]) -> None:
    wb = load_workbook(path)
    if "境界例メモ(参考)" in wb.sheetnames:
        del wb["境界例メモ(参考)"]
    ws = wb.create_sheet("境界例メモ(参考)")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 60
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 60

    styles = {
        "title": Font(size=14, bold=True, color="1F3864"),
        "h":     Font(size=11, bold=True, color="1F3864"),
        "lead":  Font(size=10, bold=True),
        "":      Font(size=10),
    }
    row = 1
    for text, kind in INTRO_LINES:
        c = ws.cell(row=row, column=1, value=text)
        c.font = styles[kind]
        c.alignment = Alignment(wrap_text=True, vertical="top")
        row += 1

    header_row = row
    header_fill = PatternFill("solid", fgColor="1F3864")
    for j, label in enumerate(["タイトル", "校正セットでの最終判定", "判断の要点"], start=1):
        c = ws.cell(row=header_row, column=j, value=label)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = header_fill
    row = header_row + 1
    for ex in examples:
        note = ex["consensus_note"].strip() or "(協議メモ未記入)"
        ws.cell(row=row, column=1, value=ex["title"]).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(row=row, column=2, value=ex["final_decision"]).alignment = Alignment(vertical="top")
        ws.cell(row=row, column=3, value=note).alignment = Alignment(wrap_text=True, vertical="top")
        row += 1

    ws.protection.sheet = True
    wb.save(path)


def main() -> None:
    examples = load_examples()
    if not examples:
        sys.exit("[ERROR] consensus_worklist.csv に対象レコードが無い(final_decision未記入?)")
    for rv in ("kataoka", "watanabe"):
        path = ROOT / "screening" / "stage2" / f"stage2_sheet_{rv}.xlsx"
        if not path.exists():
            print(f"[SKIP] {path.name} が無い")
            continue
        add_sheet(path, examples)
        print(f"[INFO] {path.name} に境界例メモを追加({len(examples)}件)")


if __name__ == "__main__":
    main()
