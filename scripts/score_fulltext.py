#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
score_fulltext.py — Phase 4(全文評価)の記入を検査し、評価者間一致度を集計する
================================================================================

【何を】
  1. 各評価者のシートの記入を検査する(未記入・語彙外の値・規則との食い違い・根拠の欠落・抽出列の欠落)
  2. 担当ペアごとに判定を突き合わせ、Cohen's κ(Include / Exclude の 2 値)と一致率、
     基準別の一致率(Y / N の 2 値。? は別集計)、Unsure の件数を出す
  3. 協議リスト `consensus_worklist.csv`(不一致・Unsure・基準の ? を含む行)を書き出す
  4. 協議の結果(final_decision)が埋まったら、`final_decisions.csv`・除外理由別の件数・
     事実の抽出表(`extraction_table.csv`)を書き出す

【κ の扱い(phase4_sheet_design.md §8)】
  - 対象は両者が Include か Exclude を付けた記録。Unsure を含む記録は「未解決」として別に数える
    (κ の分母に入れない)。κ は ペアごとと、その平均を出す。
  - 1 ペアあたり約 50 件で κ の信頼区間が広いので、一致率と基準別の不一致件数も必ず併記する。

【入力】 --dir(既定 screening/phase4)の assignment.csv と <who>/phase4_sheet_<who>.xlsx(または .csv)
【出力】 --dir の consensus_worklist.csv / (協議後)final_decisions.csv・extraction_table.csv

実行:
  python -X utf8 scripts/score_fulltext.py                 # 検査と集計
  python -X utf8 scripts/score_fulltext.py --final         # 協議後: 最終判定と抽出表を書き出す
  python -X utf8 scripts/score_fulltext.py --dir <dir>     # 検証用(別の場所を読む)

終了コード: 検査でエラー(語彙外・規則との食い違いなど)があれば 1。警告だけなら 0。
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))

csv.field_size_limit(10 ** 9)

try:
    import openpyxl
except ImportError:
    sys.exit("[ERROR] openpyxl が必要です:  pip install openpyxl")

from make_fulltext_sheets import (  # noqa: E402
    COLS, CRIT_KEYS, CRIT_LABEL, DECISIONS, EXTRACT, EXTRACT_KEYS, EXTRACT_REQUIRED,
    REASON_OTHER, REASON_VALUES, YNQ, auto_reason, expected_decision,
)
from make_screening_sheets import REVIEWERS  # noqa: E402
from score_screening import cohen_kappa, landis_koch  # noqa: E402

# 除外理由の優先順位(Rev.24)。複数の理由が割れたとき、最終の主理由はより上のものを採る。
REASON_PRIORITY = [
    "重複(同一研究の別報告)", "スコープ外(主題が無関係)", "S: 原著論文でない", "S: ユーザー実験が無い",
    "P: 対象者が不適合", "I: HMD-VR でない", "I: スケール操作/多感覚刺激が無い",
    "O: スケール知覚の測定が無い", REASON_OTHER,
]
# 6 列の基準 → 除外理由(最終の主理由を自動で提案するときの対応。C は「その他」+メモ)
CRIT_TO_REASON = {"P": "P: 対象者が不適合", "I_hmd": "I: HMD-VR でない",
                  "I_scale": "I: スケール操作/多感覚刺激が無い",
                  "O": "O: スケール知覚の測定が無い", "S": "S: ユーザー実験が無い", "C": REASON_OTHER}

MISSING_TOKENS = {"記載なし", "該当なし"}
LABEL_TO_KEY = {label: key for key, label, _w, _t in COLS}


def norm_label(s: str) -> str:
    return (s or "").replace(" ★", "").replace(" ●", "").strip()


LABEL_TO_KEY_NORM = {norm_label(l): k for l, k in LABEL_TO_KEY.items()}


def cell(v) -> str:
    return "" if v is None else str(v).strip()


# --- 読み込み ---------------------------------------------------------------
def load_sheet(path: Path) -> dict[str, dict]:
    """record_id → {キー: 値}。xlsx は「判定」シート、csv は見出しがキーまたは表示名のどちらでも読む。"""
    rows: list[list] = []
    if path.suffix.lower() == ".xlsx":
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb["判定"]
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
    else:
        with path.open(encoding="utf-8-sig", newline="") as f:
            rows = [r for r in csv.reader(f)]
    if not rows:
        return {}
    keys = []
    for h in rows[0]:
        h = cell(h)
        keys.append(h if h in {k for k, *_ in COLS} else LABEL_TO_KEY_NORM.get(norm_label(h), h))
    out = {}
    for r in rows[1:]:
        d = {k: cell(v) for k, v in zip(keys, r)}
        rid = d.get("record_id", "")
        if rid:
            # 「判定」は式の列。Excel で保存されていないファイル(式のキャッシュ値が無い)でも読めるよう、6 列から計算する。
            d["decision"] = expected_decision(d)
            if d["decision"] == "Exclude" and not d.get("reason"):
                d["reason"] = auto_reason(d)         # 自動の理由(式の値が無いとき)。手で選び直した理由はそのまま
            out[rid] = d
    return out


def find_sheet(base: Path, who: str) -> Path | None:
    for ext in (".xlsx", ".csv"):
        p = base / who / f"phase4_sheet_{who}{ext}"
        if p.exists():
            return p
    return None


def load_assignment(base: Path) -> list[dict]:
    with (base / "assignment.csv").open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# --- 検査 -------------------------------------------------------------------
def split_multi(s: str) -> list[str]:
    return [t.strip() for t in s.replace("；", ";").split(";") if t.strip()]


def check_sheet(who: str, rows: dict[str, dict], assigned: dict[str, dict]) -> tuple[list[str], list[str]]:
    """(エラー, 警告)。エラー= 値が壊れている。警告= 未記入・書き忘れ。"""
    err, warn = [], []
    vocab = {e[0]: e[4] for e in EXTRACT if e[3] in ("vocab", "multi", "ynq")}
    for rid, r in rows.items():
        tag = f"{who}:{rid}"
        if rid not in assigned:
            err.append(f"{tag} 割当表に無い記録")
            continue
        for k in CRIT_KEYS:
            if r.get(k) and r[k] not in YNQ:
                err.append(f"{tag} {CRIT_LABEL[k]} が Y/N/? でない: 「{r[k]}」")
        d = r.get("decision", "")          # load_sheet が 6 列から計算した値
        reason = r.get("reason", "")
        if reason and reason not in REASON_VALUES:
            err.append(f"{tag} 除外理由が語彙外: 「{reason}」")
        if not d:
            warn.append(f"{tag} 基準の 6 列に未記入がある(判定が出ない)")
            continue
        if d == "Exclude":
            if not reason:
                err.append(f"{tag} Exclude なのに除外理由が空")
            if not r.get("evidence"):
                err.append(f"{tag} Exclude なのに根拠(頁・引用)が空")
        elif reason:
            warn.append(f"{tag} {d} なのに除外理由が入っている: 「{reason}」")
        if reason == REASON_OTHER and r.get("C") != "N" and not r.get("memo"):
            err.append(f"{tag} 除外理由が「その他」なのにメモが空(C が N の自動の「その他」は不要)")
        # 抽出列
        if assigned[rid]["extractor"] == who and d in ("Include", "Unsure"):
            for k in EXTRACT_REQUIRED:
                if not r.get(k):
                    warn.append(f"{tag} 抽出列「{k}」が未記入(抽出担当)")
            if r.get("n_total") and not (r["n_total"].replace(".0", "").isdigit() or r["n_total"] in MISSING_TOKENS):
                err.append(f"{tag} n_total が整数でも「記載なし」でもない: 「{r['n_total']}」")
            for k, vals in vocab.items():
                v = r.get(k, "")
                if not v:
                    continue
                toks = split_multi(v) if k in ("scale_target", "non_visual", "task") else [v]
                for t in toks:
                    if t not in vals:
                        err.append(f"{tag} {k} が語彙外: 「{t}」")
        elif assigned[rid]["extractor"] != who and any(r.get(k) for k in EXTRACT_KEYS):
            warn.append(f"{tag} 抽出担当でないのに抽出列が入っている(無視する)")
    return err, warn


# --- 集計 -------------------------------------------------------------------
def fmt(x: float) -> str:
    return "nan" if isinstance(x, float) and math.isnan(x) else f"{x:.3f}"


def pair_stats(pair_rows: list[tuple[str, dict, dict]], a: str, b: str) -> dict:
    """(record_id, a の行, b の行) の一覧から、そのペアの統計を作る。"""
    both_ib = [(ra["decision"], rb["decision"]) for _rid, ra, rb in pair_rows
               if ra.get("decision") in ("Include", "Exclude") and rb.get("decision") in ("Include", "Exclude")]
    unsure = sum(1 for _rid, ra, rb in pair_rows if "Unsure" in (ra.get("decision"), rb.get("decision")))
    kappa, po, pe, n = cohen_kappa(both_ib)
    crit = {}
    for k in CRIT_KEYS:
        yn = [(ra.get(k), rb.get(k)) for _rid, ra, rb in pair_rows
              if ra.get(k) in ("Y", "N") and rb.get(k) in ("Y", "N")]
        q = sum(1 for _rid, ra, rb in pair_rows if "?" in (ra.get(k), rb.get(k)))
        crit[k] = {"n": len(yn), "agree": sum(1 for x, y in yn if x == y), "q": q,
                   "disagree": sum(1 for x, y in yn if x != y)}
    return {"n_records": len(pair_rows), "n_ib": n, "kappa": kappa, "po": po, "pe": pe,
            "unsure": unsure, "crit": crit,
            "disagree": sum(1 for x, y in both_ib if x != y)}


def build_worklist(pairs_rows: dict[str, list]) -> list[dict]:
    """協議リスト: 不一致・Unsure・基準が ? の行。"""
    out = []
    for pair, items in pairs_rows.items():
        for rid, ra, rb, a, b in items:
            da, db = ra.get("decision", ""), rb.get("decision", "")
            q = [k for k in CRIT_KEYS if "?" in (ra.get(k), rb.get(k))]
            crit_diff = [k for k in CRIT_KEYS if ra.get(k) in ("Y", "N") and rb.get(k) in ("Y", "N") and ra.get(k) != rb.get(k)]
            why = []
            if da != db:
                why.append("判定が不一致")
            if "Unsure" in (da, db):
                why.append("Unsure")
            if q:
                why.append("基準が ?: " + ",".join(q))
            if not why:
                continue
            row = {"record_id": rid, "pair": pair, "why": " / ".join(why), "criteria_disagree": ",".join(crit_diff),
                   "title": ra.get("title", "")}
            for tag, who, r in (("a", a, ra), ("b", b, rb)):
                row[f"{tag}_reviewer"] = who
                row[f"{tag}_decision"] = r.get("decision", "")
                row[f"{tag}_criteria"] = " ".join(f"{k}={r.get(k, '')}" for k in CRIT_KEYS)
                row[f"{tag}_reason"] = r.get("reason", "")
                row[f"{tag}_evidence"] = r.get("evidence", "")
                row[f"{tag}_memo"] = r.get("memo", "")
            row.update({"final_decision": "", "final_reason": "", "consensus_note": "", "third_reviewer_vote": ""})
            out.append(row)
    return out


WL_FIELDS = ["record_id", "pair", "why", "criteria_disagree", "title",
             "a_reviewer", "a_decision", "a_criteria", "a_reason", "a_evidence", "a_memo",
             "b_reviewer", "b_decision", "b_criteria", "b_reason", "b_evidence", "b_memo",
             "final_decision", "final_reason", "consensus_note", "third_reviewer_vote"]


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 4 の記入を検査し、κ と協議リストを出す")
    ap.add_argument("--dir", type=Path, default=ROOT / "screening" / "phase4")
    ap.add_argument("--final", action="store_true", help="協議後: 最終判定・除外理由別の件数・抽出表を書き出す")
    args = ap.parse_args()

    assignment = load_assignment(args.dir)
    assigned = {a["record_id"]: a for a in assignment}
    sheets: dict[str, dict[str, dict]] = {}
    for who in REVIEWERS:
        p = find_sheet(args.dir, who)
        if p is None:
            print(f"[WARN] {who} のシートが無い(未返却?): {args.dir / who}")
            continue
        sheets[who] = load_sheet(p)
        print(f"[INFO] {who}: {len(sheets[who])} 行を読み込み({p.name})")

    # --- 検査 ---
    n_err = 0
    for who, rows in sheets.items():
        err, warn = check_sheet(who, rows, assigned)
        done = sum(1 for r in rows.values() if r.get("decision"))
        print(f"\n== 検査: {who}  記入済み {done}/{len(rows)}  エラー {len(err)}  警告 {len(warn)}")
        for m in err[:40]:
            print("  [ERROR]", m)
        for m in warn[:40]:
            print("  [WARN] ", m)
        if len(err) > 40 or len(warn) > 40:
            print(f"  … 表示は各 40 件まで(エラー {len(err)} / 警告 {len(warn)})")
        n_err += len(err)

    # --- ペアごとに突き合わせ ---
    pairs_rows: dict[str, list] = defaultdict(list)
    for a in assignment:
        ra = sheets.get(a["reviewer_a"], {}).get(a["record_id"])
        rb = sheets.get(a["reviewer_b"], {}).get(a["record_id"])
        if ra and rb and ra.get("decision") and rb.get("decision"):
            pairs_rows[a["pair"]].append((a["record_id"], ra, rb, a["reviewer_a"], a["reviewer_b"]))

    print("\n== 評価者間一致度(Include / Exclude の 2 値。Unsure を含む記録は κ の分母に入れない)")
    kappas = []
    for pair, items in pairs_rows.items():
        a, b = items[0][3], items[0][4]
        st = pair_stats([(rid, ra, rb) for rid, ra, rb, _a, _b in items], a, b)
        if st["n_ib"] and not math.isnan(st["kappa"]):
            kappas.append(st["kappa"])
        print(f"  {pair}: 突き合わせ {st['n_records']} 件 / 2 値で比べた {st['n_ib']} 件 / "
              f"κ={fmt(st['kappa'])}({landis_koch(st['kappa']) if not math.isnan(st['kappa']) else '算出不可'}) / "
              f"一致率={fmt(st['po'])} / 不一致 {st['disagree']} 件 / Unsure を含む {st['unsure']} 件")
        for k in CRIT_KEYS:
            c = st["crit"][k]
            rate = c["agree"] / c["n"] if c["n"] else float("nan")
            print(f"      {CRIT_LABEL[k]:<16} 一致 {c['agree']}/{c['n']}({fmt(rate)})  不一致 {c['disagree']}  ?を含む {c['q']}")
    if kappas:
        print(f"  平均 κ = {fmt(sum(kappas) / len(kappas))}({len(kappas)} ペア)")
    elif pairs_rows:
        print("  κ を算出できるペアが無い(全件同じカテゴリ、または 2 値で比べた件数が 0)")
    else:
        print("  突き合わせられる記録がまだ無い(両者の判定が揃っていない)")

    # --- 協議リスト ---
    wpath = args.dir / "consensus_worklist.csv"
    if args.final:
        # 協議後は、書き込み済みの協議リストを読むだけ(作り直すと協議の結果が消える)
        if not wpath.exists():
            sys.exit(f"[ERROR] 協議リストが無い: {wpath}(先に --final なしで実行して協議リストを作る)")
    else:
        wl = build_worklist(pairs_rows)
        if wpath.exists():
            # 協議の結果(final_*)を書き込んでいる可能性があるので、記入済みの行は引き継ぐ
            old = {r["record_id"]: r for r in csv.DictReader(wpath.open(encoding="utf-8-sig", newline=""))}
            kept = 0
            for r in wl:
                o = old.get(r["record_id"])
                if o and any((o.get(k) or "").strip() for k in ("final_decision", "final_reason", "consensus_note",
                                                                "third_reviewer_vote")):
                    for k in ("final_decision", "final_reason", "consensus_note", "third_reviewer_vote"):
                        r[k] = o.get(k, "")
                    kept += 1
            if kept:
                print(f"\n[INFO] 既存の協議結果 {kept} 件を引き継いだ")
        write_csv(wpath, WL_FIELDS, wl)
        print(f"\n[INFO] 協議リスト: {wpath}  {len(wl)} 件(不一致 / Unsure / 基準が ?)")
        sys.exit(1 if n_err else 0)

    # --- 協議後: 最終判定 ---
    wl_done = {r["record_id"]: r for r in csv.DictReader(wpath.open(encoding="utf-8-sig", newline=""))}
    finals, problems = [], []
    for a in assignment:
        rid = a["record_id"]
        ra = sheets.get(a["reviewer_a"], {}).get(rid)
        rb = sheets.get(a["reviewer_b"], {}).get(rid)
        if a["distributed"] != "Y":
            problems.append(f"{rid} 未配布(全文未取得)。最終判定なし")
            continue
        if not (ra and rb and ra.get("decision") and rb.get("decision")):
            problems.append(f"{rid} 判定が揃っていない")
            continue
        da, db = ra["decision"], rb["decision"]
        w = wl_done.get(rid, {})
        if da == db and da in ("Include", "Exclude") and not w.get("final_decision"):
            fd, how = da, "一致"
        else:
            fd, how = (w.get("final_decision") or "").strip(), "協議"
            if fd not in ("Include", "Exclude"):
                problems.append(f"{rid} 協議の最終判定が未記入(または Include / Exclude でない): 「{fd}」")
                continue
        reason, rnote = "", ""
        if fd == "Exclude":
            reason = (w.get("final_reason") or "").strip()
            if not reason:
                rs = [r for r in (ra.get("reason"), rb.get("reason")) if r and r in REASON_VALUES]
                reason = min(rs, key=REASON_PRIORITY.index) if rs else ""
                rnote = "" if len(set(rs)) <= 1 else "(理由が割れたので優先順位で採用)"
            if not reason:
                problems.append(f"{rid} Exclude にしたが、両者とも除外理由が無い。協議リストの final_reason を記入")
        finals.append({"record_id": rid, "pair": a["pair"], "decided_by": how, "final_decision": fd,
                       "final_reason": reason, "reason_note": rnote, "a_decision": da, "b_decision": db,
                       "consensus_note": w.get("consensus_note", ""), "title": a["title"]})
    fpath = args.dir / "final_decisions.csv"
    write_csv(fpath, ["record_id", "pair", "decided_by", "final_decision", "final_reason", "reason_note",
                      "a_decision", "b_decision", "consensus_note", "title"], finals)
    cnt = Counter(f["final_decision"] for f in finals)
    print(f"\n== 最終判定: {fpath}  {len(finals)} 件  {dict(cnt)}")
    rc = Counter(f["final_reason"] for f in finals if f["final_decision"] == "Exclude")
    print("  除外理由別(PRISMA の Phase 4 除外):")
    for v in REASON_PRIORITY:
        if rc.get(v):
            print(f"    {v}: {rc[v]}")
    for m in problems:
        print("  [PROBLEM]", m)

    # --- 抽出表(Include の抽出担当の行) ---
    inc = {f["record_id"] for f in finals if f["final_decision"] == "Include"}
    ext = []
    for rid in sorted(inc):
        a = assigned[rid]
        r = sheets.get(a["extractor"], {}).get(rid, {})
        ext.append({"record_id": rid, "extractor": a["extractor"], "title": a["title"],
                    **{k: r.get(k, "") for k in EXTRACT_KEYS}})
    epath = args.dir / "extraction_table.csv"
    write_csv(epath, ["record_id", "extractor", "title"] + EXTRACT_KEYS, ext)
    miss = [e["record_id"] for e in ext if any(not e[k] for k in EXTRACT_REQUIRED)]
    print(f"  抽出表: {epath}  Include {len(ext)} 件(必須の抽出列に空欄がある行 {len(miss)} 件)")
    sys.exit(1 if (n_err or problems) else 0)


if __name__ == "__main__":
    main()
