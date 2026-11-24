"""v0.2(日本語)と v0.3(英語)の抜き出しテストの比較を Excel にまとめる(決定論的。AI は使わない)。
使い方: python -X utf8 build_compare_xlsx.py <出力.xlsx>
"""
import sys, collections, pathlib
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

AE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AE))
SRC = (AE / "build_result_xlsx.py").read_text(encoding="utf-8")
CORE = SRC[:SRC.index("wb = Workbook()")]


def load(model_dir):
    g = {"__name__": "x"}
    exec(CORE.replace("MODEL = 'claude-sonnet-5-5'", f"MODEL = {model_dir!r}"), g)
    return g


A = load("claude-sonnet-5-5")          # v0.2
Bv = load("claude-sonnet-5-5_v0.3")     # v0.3
G = Bv  # 書式の関数(head, widths, fill_rows, 色)はどちらにもある
FIELDS, FJ, ids, ass = G["FIELDS"], G["FJ"], G["ids"], G["ass"]
RED, YEL, GRN = G["RED"], G["YEL"], G["GRN"]


def summary(g):
    q, cell, meta = g["quotes"], g["cell"], g["meta"]
    stc = collections.Counter(x[5] for x in q)
    nz = [c for c in cell.values() if not c["empty_all"]]
    return dict(n=len(q), per=len(q) / (len(ids) * 3), ok=stc["OK"] + stc["WRONG_PAGE"], bad=stc["PARTLY"] + stc["ABSENT"],
                shared=sum(c["shared"] for c in nz), nz=len(nz), same=sum(c["same_text"] for c in cell.values()),
                empty=sum(c["empty_all"] for c in cell.values()),
                jac=sum(c["jac"] for c in nz) / len(nz),
                cost=sum((m["response"].get("total_cost_usd") or 0) for m in meta.values()))


def union(g):
    U = collections.defaultdict(set)
    for rid, f, k, pg, qt, st, iv in g["quotes"]:
        if iv:
            U[rid, f].update(range(*iv))
    return U


sa, sb = summary(A), summary(Bv)
UA, UB = union(A), union(Bv)
ta = sum(len(v) for v in UA.values())
tb = sum(len(v) for v in UB.values())
a_in_b = sum(len(UA[k] & UB.get(k, set())) for k in UA) / ta
b_in_a = sum(len(UB[k] & UA.get(k, set())) for k in UB) / tb
only_b_empty = sorted(k for k, c in Bv["cell"].items() if c["empty_all"] and not A["cell"][k]["empty_all"])

wb = Workbook()
ws = wb.active
ws.title = "概要"
lines = [
    ("Phase 4 該当箇所の抜き出し — 英語版プロンプト(v0.3)のテスト結果と、日本語版(v0.2)との比較", True),
    ("作成: 2026-11-24。入力は両者 Include の 33 件の全文テキスト。モデルは claude-sonnet-5-5、各版 3 回ずつ(99 回)。", False),
    ("v0.3 は v0.2 の英訳(指示の中身・17 項目・出力の形は同じ)。v0.2 の結果は 2026-11-13 のテスト(`サーベイ_Phase4_AI抜き出しテスト結果_1113.xlsx`)。", False),
    ("照合の規則は 11-13 と同じ(空白・PDF の合字・行末ハイフンの違いを無視)。テストなので、出力は抽出の記録には使わない。", False),
    ("", False),
]
for i, (t, b) in enumerate(lines, 1):
    ws.cell(i, 1, t).font = Font(bold=b, size=14 if i == 1 else 11)
r0 = len(lines) + 1
hdr = ["項目", "v0.2(日本語)", "v0.3(英語)"]
for j, h in enumerate(hdr, 1):
    c = ws.cell(r0, j, h)
    c.font = Font(bold=True, color="FFFFFF")
    c.fill = G["BLUE"]
    c.border = G["B"]
rows = [
    ("引用の数(3 回の合計)", sa["n"], sb["n"]),
    ("1 論文・1 回あたりの引用数", round(sa["per"], 1), round(sb["per"], 1)),
    ("本文と一致(頁違いを含む)", f'{sa["ok"]}({sa["ok"] / sa["n"]:.1%})', f'{sb["ok"]}({sb["ok"] / sb["n"]:.1%})'),
    ("本文と一致しない", sa["bad"], f'{sb["bad"]}(原因の分類はまだ)'),
    ("3 回すべてに共通する箇所がある組(0 件の組を除く)", f'{sa["shared"]} / {sa["nz"]}({sa["shared"] / sa["nz"]:.0%})',
     f'{sb["shared"]} / {sb["nz"]}({sb["shared"] / sb["nz"]:.0%})'),
    ("3 回で引用の集合が文字列として同じ組(561 組中)", f'{sa["same"]}({sa["same"] / 561:.0%})', f'{sb["same"]}({sb["same"] / 561:.0%})'),
    ("3 回の指す箇所の重なり(Jaccard 平均)", round(sa["jac"], 2), round(sb["jac"], 2)),
    ("3 回とも 0 件の組", sa["empty"], f'{sb["empty"]}(v0.2 の {sa["empty"]} 組をすべて含む)'),
    ("相手の版の引用範囲(文字)をどれだけ含むか", f"v0.3 の範囲の {b_in_a:.0%}", f"v0.2 の範囲の {a_in_b:.0%}"),
    ("費用(99 回)", f'{sa["cost"]:.1f} ドル', f'{sb["cost"]:.1f} ドル'),
]
for i, row in enumerate(rows, r0 + 1):
    for j, v in enumerate(row, 1):
        c = ws.cell(i, j, v)
        c.border = G["B"]
r = r0 + len(rows) + 2
notes = [
    ("読み取れること", True),
    ("・照合の一致率は同じ。英語版は引用が約 24% 少なく、範囲を絞る方向に変わった。3 回の出力はやや揃う。", False),
    (f"・英語版だけ 3 回とも 0 件になった組が {len(only_b_empty)}。日本語版の引用の多くは関係の薄い箇所だったが、"
     "Rf838e7bc8 の「拡大か縮小か」(胴とお腹を大きくし腕を太くした、の記述)は答えになる箇所で、英語版は 3 回とも挙げなかった。", False),
    ("・担当者は引用だけを読むので、抜き出しでは見落としの方が困る。どちらで本番を回すかは、範囲が大きく減った組を人が読んで決める。", False),
    ("", False),
    ("シート", True),
    ("列別の比較: 17 列それぞれの引用数・0 件の組・安定性を 2 つの版で並べた。", False),
    ("英語版だけ0件: v0.3 で 3 回とも 0 件、v0.2 では引用があった組と、v0.2 の引用。見落としかどうかを人が確かめる欄つき。", False),
    ("範囲が大きく減った組: v0.2 が引用した範囲の半分未満しか v0.3 が引用していない組。見落としの確認の候補。", False),
    ("要確認の引用(v0.3): 本文と一致しなかった v0.3 の引用。原因を人が分ける欄つき。", False),
    ("3回とも0件(v0.3): v0.3 で 3 回とも引用が出なかった組。", False),
    ("引用一覧(v0.3): v0.3 の出力した引用すべて。", False),
]
for i, (t, b) in enumerate(notes, r):
    ws.cell(i, 1, t).font = Font(bold=b, size=11)
ws.column_dimensions["A"].width = 60
ws.column_dimensions["B"].width = 28
ws.column_dimensions["C"].width = 34

# 列別の比較
ws = wb.create_sheet("列別の比較")
G["head"](ws, ["列", "内容", "引用数 v0.2", "引用数 v0.3", "3回とも0件 v0.2", "3回とも0件 v0.3",
               "共通する箇所あり v0.2", "共通する箇所あり v0.3", "集合が同じ v0.2", "集合が同じ v0.3", "v0.2 の範囲を v0.3 が含む割合"])
rows = []
for f in FIELDS:
    ca = [A["cell"][x, f] for x in ids]
    cb = [Bv["cell"][x, f] for x in ids]
    nza = [c for c in ca if not c["empty_all"]]
    nzb = [c for c in cb if not c["empty_all"]]
    tot = sum(len(UA[x, f]) for x in ids)
    inc = sum(len(UA[x, f] & UB.get((x, f), set())) for x in ids)
    rows.append([f, FJ[f], sum(1 for q in A["quotes"] if q[1] == f), sum(1 for q in Bv["quotes"] if q[1] == f),
                 sum(c["empty_all"] for c in ca), sum(c["empty_all"] for c in cb),
                 f'{sum(c["shared"] for c in nza)} / {len(nza)}', f'{sum(c["shared"] for c in nzb)} / {len(nzb)}',
                 sum(c["same_text"] for c in ca), sum(c["same_text"] for c in cb), round(inc / tot, 2) if tot else ""])
G["fill_rows"](ws, rows, {11: lambda v, r: RED if isinstance(v, float) and v < 0.5 else (YEL if isinstance(v, float) and v < 0.65 else None)})
G["widths"](ws, [20, 18, 11, 11, 12, 12, 14, 14, 12, 12, 16])
ws.freeze_panes = "C2"


def dedup(qs):
    seen, out = set(), []
    for q in qs:
        k = G["n0"](q[4])
        if k not in seen:
            seen.add(k)
            out.append(q)
    return out


# 英語版だけ 0 件
ws = wb.create_sheet("英語版だけ0件")
G["head"](ws, ["record_id", "抽出担当", "列", "内容", "v0.2 で引用があった回", "頁", "v0.2 の引用(重複を除く)", "見落としか(人)", "メモ"])
rows = []
for rid, f in only_b_empty:
    qs = [q for q in A["quotes"] if q[0] == rid and q[1] == f]
    runs = ",".join(sorted({q[2] for q in qs}))
    for q in dedup(qs):
        rows.append([rid, ass.get(rid, {}).get("extractor", ""), f, FJ[f], runs, q[3], q[4], "", ""])
G["fill_rows"](ws, rows, {8: lambda v, r: YEL, 9: lambda v, r: YEL}, wrapcols=(7,))
G["widths"](ws, [13, 11, 18, 16, 10, 6, 90, 14, 30])
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:I{len(rows) + 1}"

# 範囲が大きく減った組
ws = wb.create_sheet("範囲が大きく減った組")
G["head"](ws, ["record_id", "抽出担当", "列", "内容", "v0.2 の引用範囲(文字)", "v0.3 の引用範囲(文字)",
               "v0.2 の範囲を v0.3 が含む割合", "引用数 v0.2(3回)", "引用数 v0.3(3回)", "見落としか(人)", "メモ"])
rows = []
for (rid, f), ua in sorted(UA.items()):
    if not ua:
        continue
    ub = UB.get((rid, f), set())
    ratio = len(ua & ub) / len(ua)
    if ratio < 0.5:
        rows.append([rid, ass.get(rid, {}).get("extractor", ""), f, FJ[f], len(ua), len(ub), round(ratio, 2),
                     "/".join(map(str, A["cell"][rid, f]["n"])), "/".join(map(str, Bv["cell"][rid, f]["n"])), "", ""])
rows.sort(key=lambda r: (r[6], r[0]))
G["fill_rows"](ws, rows, {7: lambda v, r: RED if v == 0 else YEL, 10: lambda v, r: YEL, 11: lambda v, r: YEL})
G["widths"](ws, [13, 11, 18, 16, 14, 14, 14, 12, 12, 14, 30])
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:K{len(rows) + 1}"

# 要確認の引用(v0.3)
ws = wb.create_sheet("要確認の引用(v0.3)")
G["head"](ws, ["record_id", "列", "回", "頁", "照合", "引用(AI の出力そのまま)", "原因(人): AI が原文を変えた / 本文の側の問題", "メモ"])
rows = [[q[0], q[1], int(q[2]), q[3], G["SJ"][q[5]], q[4], "", ""] for q in Bv["quotes"] if q[5] in ("PARTLY", "ABSENT")]
G["fill_rows"](ws, rows, {7: lambda v, r: YEL, 8: lambda v, r: YEL}, wrapcols=(6,))
G["widths"](ws, [13, 18, 5, 6, 14, 90, 24, 30])
ws.freeze_panes = "A2"

# 3回とも0件(v0.3)
ws = wb.create_sheet("3回とも0件(v0.3)")
G["head"](ws, ["record_id", "抽出担当", "列", "内容", "v0.2 でも 0 件", "本文を確かめた結果(人)", "メモ"])
rows = [[x, ass.get(x, {}).get("extractor", ""), f, FJ[f], "○" if A["cell"][x, f]["empty_all"] else "", "", ""]
        for x in ids for f in FIELDS if Bv["cell"][x, f]["empty_all"]]
G["fill_rows"](ws, rows, {6: lambda v, r: YEL, 7: lambda v, r: YEL})
G["widths"](ws, [13, 11, 18, 16, 12, 24, 30])
ws.freeze_panes = "A2"

# 引用一覧(v0.3)
ws = wb.create_sheet("引用一覧(v0.3)")
G["head"](ws, ["record_id", "列", "内容", "回", "頁", "照合", "引用(AI の出力そのまま)"])
rows = [[q[0], q[1], FJ[q[1]], int(q[2]), q[3], G["SJ"][q[5]], q[4]] for q in Bv["quotes"]]
G["fill_rows"](ws, rows, {6: lambda v, r: None if v == G["SJ"]["OK"] else (YEL if v == G["SJ"]["WRONG_PAGE"] else RED)}, wrapcols=(7,))
G["widths"](ws, [13, 20, 18, 5, 6, 16, 110])
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:G{len(rows) + 1}"

wb.save(sys.argv[1])
print("saved", sys.argv[1], "only_b_empty", len(only_b_empty), "a_in_b", round(a_in_b, 3), "b_in_a", round(b_in_a, 3))
