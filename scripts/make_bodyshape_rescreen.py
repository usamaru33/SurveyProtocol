#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_bodyshape_rescreen.py — 体形の論文だけで Phase 3b(Title/Abstract)をやり直すための判定シートを作る
================================================================================

【何を】
  Phase 3b で Exclude になった記録のうち、題名か要旨に体形の語を含むもの(`outputs/body_shape_trace.csv` の
  stage が「P3b …」の行。61 件)を対象に、Phase 3b と同じ書式の判定シート(Excel)を評価者ごとに作る。
  書式(列・プルダウン・除外理由の統制語彙・条件付き書式・保護)は `make_screening_xlsx.py` をそのまま使う。

【なぜ】
  2026-11-19 の MTG で、体形の変化(太る・痩せる)を I_scale に含める方針になった
  (`docs/reference/body_shape_scope_analysis.md` §3・§4)。Phase 3b で「スケール操作なし」として落ちた
  体形の論文を、Rev.33 の規則で読み直す。

【手続き — Phase 3b と同じ 2 段(liberal accelerated)】
  - 第 1 段: 著者が全 61 件を判定。校正セット(20%、切り上げで 13 件)は他の 2 名も判定する(κ 用)。
    校正セットは Phase 3b と同じハッシュ md5("cal:"+key) % 100 の小さい順に取る(Phase 3b の規則の
    「% 100 < 20」をそのまま当てると 9 件=15% にしかならないため、同じ順位で件数だけ 20% に合わせた。
    Phase 3b で校正セットだった記録は必ず含まれる)。
  - 第 2 段(`--stage2`、著者の記入後): 著者が Exclude / Unsure にした記録(校正セットを除く)を、
    Phase 3b と同じ `second_reviewer_of`(md5("2nd:"+key))で Kataoka / WATANABE に振り分ける。
  - Include は 1 人で通す。2 人とも Exclude で除外。κ は校正セットで出す(13 件なので参考値。一致率を併記)。
  方法の節に「Phase 3b と同じ手続きで再判定した」と 1 文で書けるように、手続きを Phase 3b に揃えた。

【独立性】
  - 評価者ごとに別ファイル。前回の判定・除外理由はシートに入れない(引きずられないように)。
  - 第 2 段のシートにも著者の判定は入れない(Phase 3b と同じ)。
  - 前回の判定と割当は `targets.csv` にだけ残す(集計と報告用。評価者には配らない)。

【入出力】
  入力: outputs/body_shape_trace.csv、screening/stage1/sheet_author.csv(題名・要旨などのメタ)、
        screening/final/final_decisions.csv と screening/_archive/stage2/*.xlsx(前回の判定。targets.csv 用)
  出力: screening/rescreen_bodyshape/targets.csv(割当: calibration・second_reviewer と前回の判定)
        screening/rescreen_bodyshape/rescreen_sheet_<id>.xlsx(第 1 段。著者 61 件 / 他 2 名は校正セット 13 件)
        screening/rescreen_bodyshape/rescreen_stage2_sheet_<id>.xlsx(第 2 段)
        いずれの xlsx も .gitignore 対象。

実行:
  python -X utf8 scripts/make_bodyshape_rescreen.py              # 第 1 段
  python -X utf8 scripts/make_bodyshape_rescreen.py --stage2     # 第 2 段(著者の記入後)
  既存の xlsx は上書きしない。--force でも、記入済みのセルがあれば止まる。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))

csv.field_size_limit(10 ** 9)

from openpyxl import Workbook, load_workbook  # noqa: E402

import make_screening_xlsx as mx  # noqa: E402
from make_screening_sheets import CALIBRATION_PCT, REVIEWERS, SECOND_REVIEWERS, second_reviewer_of  # noqa: E402

OUT = ROOT / "screening" / "rescreen_bodyshape"

# 再判定のシートに出す列(Phase 3b の列から、校正セット・ブロックなど今回は意味の無い列を外す)
KEEP = ["record_id", "decision", "reason", "note", "title", "abstract", "venue", "year",
        "rank", "has_abstract", "calibration", "abstract_source", "doi"]

INTRO = [
    ("Phase 3b 再判定(体形の変化)  判定シート", "title"),
    ("", ""),
    ("担当: {reviewer}", "lead"),
    ("担当件数: {n:,} 件", "lead"),
    ("", ""),
    ("■ これは何か", "h"),
    ("Phase 3b(題名・要旨の判定)で除外した論文のうち、体形の語(overweight / obese / body shape /", ""),
    ("body image / belly / waist など)を含むものだけを集めました。", ""),
    ("2026-11-19 の MTG で「体形の変化(太る・痩せる)もスケールの操作に含める」方針になり、プロトコルに入れた(Rev.33)ため、", ""),
    ("新しい規則で読み直します。体形と関係のない論文(語が偶然一致しただけのもの)も混ざっています。", ""),
    ("", ""),
    ("■ 今回の I(スケール操作)の規則(プロトコル Rev.33、2026-11-21)", "h"),
    ("レンダリングされた自己身体の寸法(長さ・幅・周径)のどれかが変わる操作は、スケール操作に含める。", "lead"),
    ("全身が一様に拡大・縮小するものに限らず、方向によって倍率が違う変化(太る・痩せる・お腹だけ大きくなる)も含む。", "lead"),
    ("  次のものは、これまでどおり含めない:", ""),
    ("  ・他人のアバターの体形を見るだけ(自分の寸法は変わらない)", ""),
    ("  ・寸法が変わらない外見の変更(肌の色・性別・年齢・服装)", ""),
    ("  ・操作がなく、身体満足度などを質問紙で測るだけ", ""),
    ("それ以外の基準(P・I の HMD・O・S)は Phase 3b のときと同じです。", ""),
    ("", ""),
    ("■ やること", "h"),
    ("「判定」シートの ★ が付いた2列を埋めてください。どちらも選択式です。", ""),
    ("  ・判定 … Include(残す) / Exclude(除外) / Unsure(保留) から選ぶ", ""),
    ("  ・除外理由 … Exclude のときは必須。下の一覧から1つ選ぶ", ""),
    ("", ""),
    ("■ 除外理由の選択肢(Phase 3b と同じ)", "h"),
    ("__REASON_TABLE__", ""),
    ("当てはまるものが無ければ「その他」を選び、メモに理由を必ず書いてください。", "lead"),
    ("", ""),
    ("■ 判定の考え方(Phase 3b と同じ)", "h"),
    ("除外できると確信できないものは残してください(Include)。全文を読めば分かることを、この段階で切らないためです。", ""),
    ("__STAGE__", "lead"),
    ("方式は Phase 3b と同じ liberal accelerated です。Include は確定で全文評価(Phase 4)へ。", ""),
    ("Exclude と Unsure は第 2 評価者が確認し、2 人とも Exclude で初めて除外されます。迷ったら Unsure で構いません。", ""),
    ("前回の判定はこのシートには入れていません。前回に引きずられずに読んでください。", ""),
    ("", ""),
    ("■ お願い", "h"),
    ("他の評価者のファイルは開かないでください(評価者間一致度 κ が意味を失います)。", "warn"),
    ("", ""),
    ("■ 使い方のヒント", "h"),
    ("・見出し行は固定してあります。オートフィルタで「判定」を (空白) で絞ると未記入だけ表示できます。", ""),
    ("・要旨はセルに冒頭しか表示されません。行番号を右クリック →「行の高さの自動調整」で全文を表示できます。", ""),
    ("・入力する3列以外はロックしてあります(誤編集の防止)。", ""),
    ("", ""),
    ("■ 終わったら", "h"),
    ("このファイルを著者に渡してください。", ""),
]


STAGE_NOTE = {
    "author": "このシートは第 1 段(全件)です。「校正セット」列が Y の論文は、他の 2 名も同じものを判定します。",
    "calibration": "このシートは校正セット(全体の 20%)です。3 名全員が同じ論文を判定し、評価者間一致度(κ)を出します。",
    "stage2": "このシートは第 2 段です。第 1 段で Include にならなかった論文を確認してください。",
}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def stage2_decisions() -> dict[str, dict]:
    """_archive/stage2 の提出シートから、第 2 評価者の判定・理由を読む(targets.csv の記録用)。"""
    out: dict[str, dict] = {}
    for p in sorted((ROOT / "screening" / "_archive" / "stage2").glob("stage2_sheet_*.xlsx")):
        who = p.stem.split("_")[2]
        ws = load_workbook(p, read_only=True, data_only=True)["判定"]
        rows = ws.iter_rows(values_only=True)
        head = [str(h or "") for h in next(rows)]
        i_id, i_d, i_r, i_m = (head.index(h) for h in ("ID", "判定 ★", "除外理由 ★", "メモ"))
        for r in rows:
            if r[i_id]:
                out[str(r[i_id])] = {"who": who, "decision": r[i_d] or "", "reason": r[i_r] or "",
                                     "memo": r[i_m] or ""}
    return out


def calibration_ids(trace: list[dict]) -> set[str]:
    """校正セット(全件の 20%、切り上げ)。Phase 3b と同じハッシュ md5("cal:"+key) % 100 の小さい順に取る。

    Phase 3b の規則(% 100 < 20)をそのまま当てると 61 件中 9 件(15%)にしかならないので、
    同じハッシュの順位で件数だけ 20% に合わせる。Phase 3b で校正セットだった記録は必ず含まれる(単調)。
    """
    n = math.ceil(len(trace) * CALIBRATION_PCT / 100)
    def h(t):
        v = int(hashlib.md5(("cal:" + t["Key"]).encode("utf-8")).hexdigest(), 16)
        return (v % 100, v)
    return {t["rid"] for t in sorted(trace, key=h)[:n]}


def build_targets(trace, meta) -> list[dict]:
    final = {r["record_id"]: r for r in read_csv(ROOT / "screening" / "final" / "final_decisions.csv")}
    s2 = stage2_decisions()
    cal = calibration_ids(trace)
    targets = []
    for t in sorted(trace, key=lambda t: t["rid"]):
        m = meta[t["rid"]]
        f = final.get(t["rid"])
        s = s2.get(t["rid"], {})
        if f:
            prev = (f"最終 {f['final_decision']}(協議リスト: {f['reviewer_a']}={f['decision_a']} {f['reason_a']} / "
                    f"{f['reviewer_b']}={f['decision_b']} {f['reason_b']})")
        else:
            prev = "協議リスト外(stage 1 の著者と stage 2 の第 2 評価者がともに Exclude)"
        c = t["rid"] in cal
        targets.append({"record_id": t["rid"], "calibration": "Y" if c else "N",
                        "second_reviewer": "" if c else second_reviewer_of(t["Key"]),
                        "title": m["title"], "venue": m["venue"], "year": m["year"],
                        "doi": m["doi"], "shape_terms": t["terms"], "p3b_previous": prev,
                        "stage2_reviewer": s.get("who", ""), "stage2_decision": s.get("decision", ""),
                        "stage2_reason": s.get("reason", ""), "stage2_memo": s.get("memo", "")})
    return targets


def write_sheet(dst: Path, who: str, rows: list[dict], force: bool, stage: str) -> None:
    if dst.exists() and not force:
        print(f"[SKIP] {dst.name} は既にある(作り直すなら --force。記入済みは失われる)")
        return
    if dst.exists():
        ws = load_workbook(dst, data_only=True)["判定"]
        filled = sum(1 for r in range(2, ws.max_row + 1) for c in (2, 3, 4) if ws.cell(r, c).value)
        if filled:
            sys.exit(f"[ERROR] {dst.name} に記入済みのセルが {filled} 個ある。上書きしない")
    mx.INTRO = [(STAGE_NOTE[stage] if text == "__STAGE__" else text, kind) for text, kind in INTRO]
    wb = Workbook()
    intro = wb.active
    intro.title = "はじめに"
    mx.build_intro(intro, REVIEWERS[who], len(rows))
    mx.build_sheet(wb.create_sheet("判定"), rows)
    wb.active = 1
    wb.save(dst)
    print(f"[INFO] 出力: {dst.name}  {len(rows)} 行  担当={REVIEWERS[who]}")


def sheet_row(m: dict, cal: bool) -> dict:
    row = {k: ("" if k in ("decision", "reason", "note") else m.get(k, "")) for k in KEEP}
    row["calibration"] = "Y" if cal else "N"
    return row


def main() -> None:
    ap = argparse.ArgumentParser(description="体形の論文だけの Phase 3b 再判定シートを作る(Phase 3b と同じ 2 段)")
    ap.add_argument("--stage2", action="store_true",
                    help="著者の記入後: 著者が Exclude / Unsure にした記録(校正セットを除く)を第 2 評価者へ")
    ap.add_argument("--force", action="store_true", help="既存の xlsx を上書きする(記入済みがあれば止まる)")
    args = ap.parse_args()

    trace = [r for r in read_csv(ROOT / "outputs" / "body_shape_trace.csv") if r["stage"].startswith("P3b")]
    meta = {r["record_id"]: r for r in read_csv(ROOT / "screening" / "stage1" / "sheet_author.csv")}
    missing = [t["rid"] for t in trace if t["rid"] not in meta]
    if missing:
        sys.exit(f"[ERROR] 判定シートのメタに無い記録: {missing}")

    OUT.mkdir(parents=True, exist_ok=True)
    mx.COLUMNS = [c for c in mx.COLUMNS if c[0] in KEEP]
    tpath = OUT / "targets.csv"

    if not args.stage2:
        targets = build_targets(trace, meta)
        with tpath.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(targets[0]))
            w.writeheader()
            w.writerows(targets)
        cal = [t for t in targets if t["calibration"] == "Y"]
        print(f"[INFO] 対象 {len(targets)} 件(校正セット {len(cal)} 件)→ {tpath.relative_to(ROOT)}")
        # stage 1: 著者は全件、他の 2 名は校正セットだけ
        all_rows = [sheet_row(meta[t["record_id"]], t["calibration"] == "Y") for t in targets]
        cal_rows = [r for r in all_rows if r["calibration"] == "Y"]
        write_sheet(OUT / "rescreen_sheet_author.xlsx", "author", all_rows, args.force, "author")
        for who in SECOND_REVIEWERS:
            write_sheet(OUT / f"rescreen_sheet_{who}.xlsx", who, cal_rows, args.force, "calibration")
        print("[NEXT] 著者の記入が終わったら --stage2 で第 2 段のシートを作る")
        return

    # stage 2: 著者が Exclude / Unsure にしたもの(校正セットは既に 3 名が判定済みなので除く)
    targets = {t["record_id"]: t for t in read_csv(tpath)}
    ws = load_workbook(OUT / "rescreen_sheet_author.xlsx", data_only=True)["判定"]
    head = [str(c.value or "") for c in ws[1]]
    i_id, i_d = head.index("ID"), head.index("判定 ★")
    author = {str(r[i_id]): (r[i_d] or "").strip() for r in ws.iter_rows(min_row=2, values_only=True) if r[i_id]}
    blank = [k for k, v in author.items() if not v]
    if blank:
        sys.exit(f"[ERROR] 著者シートに未記入が {len(blank)} 件。第 1 段を終えてから実行する")
    per = {w: [] for w in SECOND_REVIEWERS}
    for rid, d in sorted(author.items()):
        t = targets[rid]
        if t["calibration"] == "Y" or d == "Include":
            continue
        per[t["second_reviewer"]].append(sheet_row(meta[rid], False))
    n_inc = sum(1 for k, d in author.items() if d == "Include" and targets[k]["calibration"] == "N")
    print(f"[INFO] 著者: Include {n_inc} 件は 1 人で通す / 第 2 評価者へ: "
          + " / ".join(f"{REVIEWERS[w]} {len(v)} 件" for w, v in per.items()))
    for who, rows in per.items():
        if rows:
            write_sheet(OUT / f"rescreen_stage2_sheet_{who}.xlsx", who, rows, args.force, "stage2")


if __name__ == "__main__":
    main()
