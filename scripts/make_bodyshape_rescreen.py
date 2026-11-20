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
  体形の論文を、新しい規則で 2 名が要旨を読み直す。方式は Phase 3b と同じ(1 人が Include なら通す)。

【独立性】
  - 評価者ごとに別ファイル。前回の判定・除外理由はシートに入れない(引きずられないように)。
  - 前回の判定は `targets.csv` にだけ残す(集計と報告用。評価者には配らない)。

【入出力】
  入力: outputs/body_shape_trace.csv、screening/stage1/sheet_author.csv(題名・要旨などのメタ)、
        screening/final/final_decisions.csv と screening/_archive/stage2/*.xlsx(前回の判定。targets.csv 用)
  出力: screening/rescreen_bodyshape/targets.csv
        screening/rescreen_bodyshape/rescreen_sheet_<id>.xlsx(.gitignore 対象)

実行:
  python -X utf8 scripts/make_bodyshape_rescreen.py              # 3 人分
  python -X utf8 scripts/make_bodyshape_rescreen.py --only kataoka
  既存の xlsx は上書きしない(記入済みを壊さないため)。作り直すなら --force。
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))

csv.field_size_limit(10 ** 9)

from openpyxl import Workbook, load_workbook  # noqa: E402

import make_screening_xlsx as mx  # noqa: E402
from make_screening_sheets import REVIEWERS  # noqa: E402

OUT = ROOT / "screening" / "rescreen_bodyshape"

# 再判定のシートに出す列(Phase 3b の列から、校正セット・ブロックなど今回は意味の無い列を外す)
KEEP = ["record_id", "decision", "reason", "note", "title", "abstract", "venue", "year",
        "rank", "has_abstract", "abstract_source", "doi"]

INTRO = [
    ("Phase 3b 再判定(体形の変化)  判定シート", "title"),
    ("", ""),
    ("担当: {reviewer}", "lead"),
    ("担当件数: {n:,} 件", "lead"),
    ("", ""),
    ("■ これは何か", "h"),
    ("Phase 3b(題名・要旨の判定)で除外した論文のうち、体形の語(overweight / obese / body shape /", ""),
    ("body image / belly / waist など)を含むものだけを集めました。", ""),
    ("2026-11-19 の MTG で「体形の変化(太る・痩せる)もスケールの操作に含める」方針になったため、", ""),
    ("新しい規則で読み直します。体形と関係のない論文(語が偶然一致しただけのもの)も混ざっています。", ""),
    ("", ""),
    ("■ 今回の I(スケール操作)の規則  ※案。MTG で確定するまでは、この案で判定してください", "h"),
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
    ("1 人が Include なら全文評価(Phase 4)に進みます。迷ったら Unsure で構いません。", ""),
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


def main() -> None:
    ap = argparse.ArgumentParser(description="体形の論文だけの Phase 3b 再判定シートを作る")
    ap.add_argument("--only", default="", help="特定の評価者だけ(author / kataoka / watanabe)")
    ap.add_argument("--force", action="store_true", help="既存の xlsx を上書きする(記入済みは失われる)")
    args = ap.parse_args()

    trace = [r for r in read_csv(ROOT / "outputs" / "body_shape_trace.csv") if r["stage"].startswith("P3b")]
    meta = {r["record_id"]: r for r in read_csv(ROOT / "screening" / "stage1" / "sheet_author.csv")}
    final = {r["record_id"]: r for r in read_csv(ROOT / "screening" / "final" / "final_decisions.csv")}
    s2 = stage2_decisions()

    missing = [t["rid"] for t in trace if t["rid"] not in meta]
    if missing:
        sys.exit(f"[ERROR] 判定シートのメタに無い記録: {missing}")

    rows, targets = [], []
    for t in sorted(trace, key=lambda t: t["rid"]):
        m = meta[t["rid"]]
        rows.append({k: ("" if k in ("decision", "reason", "note") else m.get(k, "")) for k in KEEP})
        f = final.get(t["rid"])
        s = s2.get(t["rid"], {})
        if f:
            prev = (f"最終 {f['final_decision']}(協議リスト: {f['reviewer_a']}={f['decision_a']} {f['reason_a']} / "
                    f"{f['reviewer_b']}={f['decision_b']} {f['reason_b']})")
        else:
            prev = "協議リスト外(stage 1 の著者と stage 2 の第 2 評価者がともに Exclude)"
        targets.append({"record_id": t["rid"], "title": m["title"], "venue": m["venue"], "year": m["year"],
                        "doi": m["doi"], "shape_terms": t["terms"], "p3b_previous": prev,
                        "stage2_reviewer": s.get("who", ""), "stage2_decision": s.get("decision", ""),
                        "stage2_reason": s.get("reason", ""), "stage2_memo": s.get("memo", "")})

    OUT.mkdir(parents=True, exist_ok=True)
    tpath = OUT / "targets.csv"
    with tpath.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(targets[0]))
        w.writeheader()
        w.writerows(targets)
    print(f"[INFO] 対象 {len(targets)} 件 → {tpath.relative_to(ROOT)}")

    # Phase 3b の書式をそのまま使い、列と説明だけ差し替える
    mx.COLUMNS = [c for c in mx.COLUMNS if c[0] in KEEP]
    mx.INTRO = INTRO
    for who in ([args.only] if args.only else list(REVIEWERS)):
        if who not in REVIEWERS:
            sys.exit(f"[ERROR] 未知の評価者: {who}")
        dst = OUT / f"rescreen_sheet_{who}.xlsx"
        if dst.exists() and not args.force:
            print(f"[SKIP] {dst.name} は既にある(作り直すなら --force)")
            continue
        wb = Workbook()
        intro = wb.active
        intro.title = "はじめに"
        mx.build_intro(intro, REVIEWERS[who], len(rows))
        mx.build_sheet(wb.create_sheet("判定"), rows)
        wb.active = 1
        wb.save(dst)
        print(f"[INFO] 出力: {dst.relative_to(ROOT)}  {len(rows)} 行  担当={REVIEWERS[who]}")


if __name__ == "__main__":
    main()
