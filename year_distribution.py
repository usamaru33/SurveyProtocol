# -*- coding: utf-8 -*-
"""
year_distribution.py
====================
step3_kw_included.csv (1,784件) の発行年分布を可視化する。
  - 総計の棒グラフ
  - 各データベース（ACM / IEEE / Scopus-Elsevier / Others）別の積み上げ棒グラフ
  - 各データベース個別の折れ線グラフ

出力: year_distribution.png (同ディレクトリに保存)
"""

import re
import sys
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec
from pathlib import Path

# --------------------------------------------------------------------------
# 設定
# --------------------------------------------------------------------------
CSV_PATH   = Path("step3_kw_included.csv")
OUTPUT_PNG = Path("year_distribution.png")

# フォント設定（英語フォントのみ使用してエラー回避）
matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["axes.unicode_minus"] = False

# カラーパレット
DB_COLORS = {
    "ACM":             "#E63946",   # 赤
    "IEEE":            "#457B9D",   # 青
    "Scopus/Elsevier": "#2A9D8F",   # 緑
    "Others/Unknown":  "#E9C46A",   # 黄
}

# --------------------------------------------------------------------------
# データ読み込み & 前処理
# --------------------------------------------------------------------------
df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", low_memory=False)
TOTAL = len(df)
print(f"Loaded: {TOTAL:,} records")

# 発行年
df["_year"] = pd.to_numeric(df.get("Publication Year"), errors="coerce")

# --------------------------------------------------------------------------
# データベース分類（simulate_screening.py と同じロジック）
# --------------------------------------------------------------------------
url_s = df["Url"].fillna("").str.lower()
doi_s = df["DOI"].fillna("").str.lower()
pub_s = df["Publisher"].fillna("").str.lower() if "Publisher" in df.columns else pd.Series([""] * TOTAL, index=df.index)

def classify_db(url, doi, pub):
    if "dl.acm.org" in url or doi.startswith("10.1145"):
        return "ACM"
    if "ieeexplore.ieee.org" in url or doi.startswith("10.1109"):
        return "IEEE"
    if ("scopus.com" in url or "sciencedirect.com" in url
            or doi.startswith("10.1016")
            or "elsevier" in pub or "springer" in pub):
        return "Scopus/Elsevier"
    if ("pubmed.ncbi.nlm.nih.gov" in url or "apa.org" in url
            or "ncbi.nlm.nih.gov" in url
            or doi.startswith("10.1037")):
        return "PubMed/PsycInfo"
    return "Others/Unknown"

df["_db"] = [classify_db(u, d, p) for u, d, p in zip(url_s, doi_s, pub_s)]

# PubMed/PsycInfo が 0 件のため Others に統合
df["_db"] = df["_db"].replace("PubMed/PsycInfo", "Others/Unknown")

DB_ORDER = ["ACM", "IEEE", "Scopus/Elsevier", "Others/Unknown"]

# --------------------------------------------------------------------------
# 集計
# --------------------------------------------------------------------------
# 発行年の範囲（年が確定しているレコードのみ）
df_valid = df.dropna(subset=["_year"]).copy()
df_valid["_year"] = df_valid["_year"].astype(int)

year_min = int(df_valid["_year"].min())
year_max = int(df_valid["_year"].max())
all_years = list(range(year_min, year_max + 1))

# 総計
total_by_year = df_valid.groupby("_year").size().reindex(all_years, fill_value=0)

# DB別
db_by_year = {}
for db in DB_ORDER:
    sub = df_valid[df_valid["_db"] == db]
    db_by_year[db] = sub.groupby("_year").size().reindex(all_years, fill_value=0)

# テキスト集計を表示
print()
print("=" * 60)
print("  Year Distribution Summary")
print("=" * 60)
print(f"  {'Year':<6} {'Total':>6}", end="")
for db in DB_ORDER:
    print(f"  {db[:12]:>13}", end="")
print()
print(f"  {'-'*6} {'-'*6}", end="")
for db in DB_ORDER:
    print(f"  {'-'*13}", end="")
print()
for y in all_years:
    tot = int(total_by_year[y])
    if tot == 0:
        continue
    print(f"  {y:<6} {tot:>6}", end="")
    for db in DB_ORDER:
        print(f"  {int(db_by_year[db][y]):>13}", end="")
    print()
print(f"  {'Total':<6} {total_by_year.sum():>6}", end="")
for db in DB_ORDER:
    print(f"  {int(db_by_year[db].sum()):>13}", end="")
print()
print()

# DB合計・割合
print("  Database Totals:")
for db in DB_ORDER:
    cnt = int(db_by_year[db].sum())
    print(f"    {db:<22} : {cnt:>5,}  ({cnt/TOTAL*100:.1f}%)")
na_cnt = int(df["_year"].isna().sum())
print(f"  Year unknown: {na_cnt} records (excluded from plot)")

# --------------------------------------------------------------------------
# プロット
# --------------------------------------------------------------------------
fig = plt.figure(figsize=(18, 28))
fig.patch.set_facecolor("#0F1117")

gs = GridSpec(4, 2, figure=fig,
              hspace=0.60, wspace=0.35,
              top=0.94, bottom=0.04, left=0.08, right=0.97)

AX_STYLE = dict(facecolor="#1A1D27", grid_color="#2E3347",
                spine_color="#2E3347", text_color="#E0E0E0",
                tick_color="#A0A8C0")

def style_ax(ax):
    ax.set_facecolor(AX_STYLE["facecolor"])
    ax.tick_params(colors=AX_STYLE["tick_color"], labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor(AX_STYLE["spine_color"])
    ax.yaxis.grid(True, color=AX_STYLE["grid_color"], linestyle="--", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    ax.xaxis.label.set_color(AX_STYLE["text_color"])
    ax.yaxis.label.set_color(AX_STYLE["text_color"])
    ax.title.set_color(AX_STYLE["text_color"])

bar_width = 0.72
x = range(len(all_years))
xlabels = [str(y) for y in all_years]

# ── Panel 1: Total (span 2 columns) ─────────────────────────────────────
ax_total = fig.add_subplot(gs[0, :])
bars = ax_total.bar(x, total_by_year.values,
                    width=bar_width, color="#7B9FFF",
                    edgecolor="#0F1117", linewidth=0.4, zorder=3)
# 値ラベル（5以上のみ）
for bar, val in zip(bars, total_by_year.values):
    if val >= 5:
        ax_total.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                      str(int(val)), ha="center", va="bottom",
                      fontsize=7.5, color="#B0C0FF", fontweight="bold")
ax_total.set_xticks(list(x))
ax_total.set_xticklabels(xlabels, rotation=55, ha="right", fontsize=8.5)
ax_total.set_title(f"Total Papers by Year  (N = {TOTAL:,})",
                   fontsize=13, fontweight="bold", pad=10)
ax_total.set_ylabel("Number of Papers", fontsize=10)
ax_total.set_xlim(-0.8, len(all_years) - 0.2)
style_ax(ax_total)

# ── Panel 2: Stacked bar (span 2 columns) ───────────────────────────────
ax_stack = fig.add_subplot(gs[1, :])
bottoms = [0] * len(all_years)
for db in DB_ORDER:
    vals = db_by_year[db].values
    ax_stack.bar(x, vals, width=bar_width, bottom=bottoms,
                 label=db, color=DB_COLORS[db],
                 edgecolor="#0F1117", linewidth=0.3, zorder=3)
    bottoms = [b + v for b, v in zip(bottoms, vals)]

ax_stack.set_xticks(list(x))
ax_stack.set_xticklabels(xlabels, rotation=55, ha="right", fontsize=8.5)
ax_stack.set_title("Papers by Year — Stacked by Database Source",
                   fontsize=13, fontweight="bold", pad=10)
ax_stack.set_ylabel("Number of Papers", fontsize=10)
ax_stack.set_xlim(-0.8, len(all_years) - 0.2)
legend = ax_stack.legend(loc="upper left", fontsize=9,
                          framealpha=0.25, edgecolor="#555",
                          facecolor="#1A1D27", labelcolor="#E0E0E0")
style_ax(ax_stack)

# ── Panels 3-6: Individual DB line charts (rows 2-3, 2x2 grid) ─────────
all_db_axes = []

for idx, db in enumerate(DB_ORDER):
    row = 2 + idx // 2
    col = idx % 2
    ax = fig.add_subplot(gs[row, col])
    all_db_axes.append(ax)
    vals = db_by_year[db].values
    color = DB_COLORS[db]

    # area fill
    ax.fill_between(list(x), vals, alpha=0.18, color=color, zorder=2)
    ax.plot(list(x), vals, color=color, linewidth=2.2, marker="o",
            markersize=4, zorder=3)

    ax.set_xticks(list(x)[::2])
    ax.set_xticklabels(xlabels[::2], rotation=55, ha="right", fontsize=8)
    db_total = int(sum(vals))
    ax.set_title(f"{db}  (n = {db_total:,})",
                 fontsize=11, fontweight="bold", pad=8, color=color)
    ax.set_ylabel("Papers", fontsize=9)
    ax.set_xlim(-0.5, len(all_years) - 0.5)
    ax.set_ylim(0, max(vals) * 1.15 + 1)
    style_ax(ax)

# ── Figure title ────────────────────────────────────────────────────────
fig.suptitle("Year Distribution of Screened Literature  (Phase 3 Output)",
             fontsize=15, fontweight="bold", color="#E8ECFF", y=0.975)

plt.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print(f"Saved -> {OUTPUT_PNG.resolve()}")
plt.close()
