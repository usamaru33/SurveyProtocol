# -*- coding: utf-8 -*-
"""
simulate_screening.py
=====================
step3_kw_included.csv に対して以下を実行（読み取り専用・出力ファイルなし）

  タスク1A: 引用数による足切りシミュレーション
  タスク1B: キーワードスコアによる足切りシミュレーション
  タスク2 : 取得元データベースの集計
"""
import sys
import re
import io
import pandas as pd

# Windows cp932 環境でも絵文字・特殊文字を安全に出力するため utf-8 ラッパー
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─── データ読み込み ─────────────────────────────────────────────────────────────
CSV_PATH = "step3_kw_included.csv"
df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", low_memory=False)
TOTAL = len(df)

print("=" * 70)
print(f"  入力ファイル : {CSV_PATH}")
print(f"  総件数       : {TOTAL:,} 件")
print("=" * 70)

# ─── 利用列の確認 ─────────────────────────────────────────────────────────────
CITE_COL_CANDIDATES = ["Citation Count", "Cited by", "Citations", "Times Cited"]
CITE_COL = next((c for c in CITE_COL_CANDIDATES if c in df.columns), None)

YEAR_COL  = "Publication Year" if "Publication Year" in df.columns else None
TITLE_COL = "Title" if "Title" in df.columns else None
ABS_COL   = "Abstract Note" if "Abstract Note" in df.columns else (
             "Abstract" if "Abstract" in df.columns else None)
URL_COL   = "Url" if "Url" in df.columns else None
DOI_COL   = "DOI" if "DOI" in df.columns else None
PUB_COL   = "Publisher" if "Publisher" in df.columns else None

# ─────────────────────────────────────────────────────────────────────────────
# タスク 1A: 引用数による足切りシミュレーション
# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 70)
print("  タスク 1A: 引用数による足切りシミュレーション")
print("=" * 70)

if CITE_COL is None:
    print()
    print("  [注意] このCSVにはZotero標準の引用数列が存在しません。")
    print("    (候補列を検索: Citation Count / Cited by / Citations / Times Cited)")
    print()
    print("  代替措置: 全件の引用数を「不明 (NA -> 0 扱い)」として処理します。")
    print("  フェイルセーフ: 発行年が2023年以降の文献は足切り対象から除外します。")
    print()
    df["_cite"] = 0
    df["_cite_is_na"] = True
else:
    df["_cite"] = pd.to_numeric(df[CITE_COL], errors="coerce")
    df["_cite_is_na"] = df["_cite"].isna()
    df["_cite"] = df["_cite"].fillna(0).astype(int)
    na_count = df["_cite_is_na"].sum()
    print(f"  引用数列 '{CITE_COL}' を使用")
    print(f"    引用数 NA の件数 : {na_count:,} 件 (-> 0 として扱い集計)")

if YEAR_COL:
    df["_year"] = pd.to_numeric(df[YEAR_COL], errors="coerce")
else:
    df["_year"] = float("nan")

RECENT_YEAR = 2023  # このフェイルセーフ年以降は引用数不問で残存

def citation_simulation(df, threshold):
    is_recent = df["_year"] >= RECENT_YEAR
    excluded_mask = (df["_cite"] < threshold) & (~is_recent)
    n_excluded = excluded_mask.sum()
    n_retained = TOTAL - n_excluded
    if CITE_COL is None:
        n_recent_saved = is_recent.sum()  # 全件NA=0のため近年論文は全件救済
    else:
        n_recent_saved = ((df["_cite"] < threshold) & is_recent).sum()
    return int(n_excluded), int(n_retained), int(n_recent_saved)

THRESHOLDS = [5, 10, 20]

if CITE_COL is None:
    print("  ※ 引用数が全件不明(0扱い)のため、以下は最悪ケースのシミュレーションです。")
    print("    実際の運用では Semantic Scholar 等から引用数を取得することを推奨します。")

print()
print(f"  フェイルセーフ: 発行年 {RECENT_YEAR} 年以降の論文は引用数不問で残存")
print()
print(f"  {'閾値':<12} {'除外件数':>8} {'残存件数':>8} {'残存率':>8}  {'フェイルセーフ救済':>12}")
print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8}  {'-'*12}")

for thr in THRESHOLDS:
    excl, ret, saved = citation_simulation(df, thr)
    rate = ret / TOTAL * 100
    print(f"  引用数 < {thr:<3}  {excl:>8,} {ret:>8,} {rate:>7.1f}%  {saved:>12,}")

print()
if CITE_COL is None and YEAR_COL:
    recent = int((df["_year"] >= RECENT_YEAR).sum())
    older  = int((df["_year"] < RECENT_YEAR).sum())
    na_yr  = int(df["_year"].isna().sum())
    print("  --- 補足: 年代別 内訳 ---")
    print(f"    2023年以降 (フェイルセーフ対象) : {recent:,} 件")
    print(f"    2022年以前 (足切り対象になりうる): {older:,} 件")
    print(f"    発行年 不明                     : {na_yr:,} 件")

# ─────────────────────────────────────────────────────────────────────────────
# タスク 1B: キーワードスコアによる足切りシミュレーション
# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 70)
print("  タスク 1B: キーワードスコアによる足切りシミュレーション")
print("=" * 70)
print()

if TITLE_COL and ABS_COL:
    df["_text"] = (df[TITLE_COL].fillna("") + " " + df[ABS_COL].fillna("")).str.lower()
    abs_missing = int(df[ABS_COL].isna().sum())
    print(f"  使用列: '{TITLE_COL}' + '{ABS_COL}'")
    print(f"    Abstract が空欄の件数: {abs_missing:,} 件 (Titleのみで判定)")
elif TITLE_COL:
    df["_text"] = df[TITLE_COL].fillna("").str.lower()
    print(f"  使用列: '{TITLE_COL}' のみ (Abstract列が見つかりません)")
else:
    df["_text"] = ""
    print("  [警告] Title列も見つかりません。スコアは全件0になります。")

CATEGORIES = {
    "Cat1_VR環境    ": [
        "virtual reality", r"\bvr\b", r"\bhmd\b", "virtual environment"
    ],
    "Cat2_身体化    ": [
        "body ownership", "embodiment", r"\bavatar\b", "virtual body"
    ],
    "Cat3_スケール知覚": [
        "size perception", "body size", "eye height",
        "perceived size", "spatial scale", "scale perception"
    ],
}

def match_category(text_series, patterns):
    combined = "|".join(patterns)
    return text_series.str.contains(combined, regex=True, na=False).astype(int)

cat_keys = list(CATEGORIES.keys())
for cat_name, patterns in CATEGORIES.items():
    df[f"_score_{cat_name}"] = match_category(df["_text"], patterns)

score_cols = [f"_score_{c}" for c in cat_keys]
df["_kw_score"] = df[score_cols].sum(axis=1)

print()
print("  [カテゴリ別ヒット件数]")
print(f"  {'カテゴリ':<22} {'ヒット件数':>10} {'ヒット率':>8}")
print(f"  {'-'*22} {'-'*10} {'-'*8}")
for cat_name in cat_keys:
    hits = int(df[f"_score_{cat_name}"].sum())
    print(f"  {cat_name:<22} {hits:>10,}  {hits/TOTAL*100:>7.1f}%")

print()
print("  [スコア別 件数内訳 (0〜3点)]")
print(f"  {'スコア':<8} {'件数':>8} {'割合':>8}  解釈")
print(f"  {'-'*8} {'-'*8} {'-'*8}  {'─'*38}")
interpretations = {
    0: "全カテゴリ不一致 -> 最優先除外候補",
    1: "1カテゴリのみ一致 -> 除外候補",
    2: "2カテゴリ一致 -> 要精査",
    3: "全カテゴリ一致 -> 残存 (コアトピック)",
}
score_counts = df["_kw_score"].value_counts().sort_index()
for score in range(4):
    cnt = int(score_counts.get(score, 0))
    pct = cnt / TOTAL * 100
    interp = interpretations[score]
    print(f"  {score}点      {cnt:>8,}  {pct:>7.1f}%  {interp}")

print()
print("  [足切りシミュレーション: スコア閾値別 残存/除外件数]")
print(f"  {'足切り条件':<22} {'除外件数':>8} {'残存件数':>8} {'残存率':>8}")
print(f"  {'-'*22} {'-'*8} {'-'*8} {'-'*8}")
for cut in [1, 2]:
    excl = int((df["_kw_score"] < cut).sum())
    ret  = TOTAL - excl
    label = f"スコア < {cut}点を除外"
    print(f"  {label:<22} {excl:>8,} {ret:>8,} {ret/TOTAL*100:>7.1f}%")

# ─── A×B クロス集計 ───
print()
print("  [タスク1A × 1B クロス集計マトリクス]")
print("  (行: 引用数足切り判定, 列: KWスコア)")
print("  ※ 引用数列なし -> 全件0扱い + フェイルセーフ(2023年以降)込みの最悪ケース")
print()

for thr in THRESHOLDS:
    excl_cite = (df["_cite"] < thr) & (df["_year"] < RECENT_YEAR)
    print(f"  -- 引用数 < {thr} (フェイルセーフ適用) --")
    hdr = f"  {'':22s} {'KW=0':>8} {'KW=1':>8} {'KW=2':>8} {'KW=3':>8} {'合計':>8}"
    print(hdr)
    print(f"  {'-'*62}")
    for cite_label, cite_mask in [
        ("除外(引用数不足)", excl_cite),
        ("残存(引用数OK) ", ~excl_cite)
    ]:
        row = [int(((df["_kw_score"] == s) & cite_mask).sum()) for s in range(4)]
        total_row = sum(row)
        row_str = "".join(f"{v:>8,}" for v in row)
        print(f"  {cite_label:<22}{row_str} {total_row:>8,}")
    print()

# ─────────────────────────────────────────────────────────────────────────────
# タスク 2: 取得元データベースの集計
# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 70)
print("  タスク 2: 取得元データベースの集計")
print("=" * 70)
print()

url_col_val = df[URL_COL].fillna("").str.lower() if URL_COL else pd.Series([""] * TOTAL, index=df.index)
doi_col_val = df[DOI_COL].fillna("").str.lower() if DOI_COL else pd.Series([""] * TOTAL, index=df.index)
pub_col_val = df[PUB_COL].fillna("").str.lower() if PUB_COL else pd.Series([""] * TOTAL, index=df.index)

def classify_db(url, doi, pub):
    # ACM
    if "dl.acm.org" in url or doi.startswith("10.1145"):
        return "ACM"
    # IEEE
    if "ieeexplore.ieee.org" in url or doi.startswith("10.1109"):
        return "IEEE"
    # Scopus / Elsevier / Springer
    if ("scopus.com" in url or "sciencedirect.com" in url
            or doi.startswith("10.1016")
            or "elsevier" in pub or "springer" in pub):
        return "Scopus/Elsevier"
    # PubMed / PsycInfo (APA)
    if ("pubmed.ncbi.nlm.nih.gov" in url or "apa.org" in url
            or "ncbi.nlm.nih.gov" in url
            or doi.startswith("10.1037")):
        return "PubMed/PsycInfo"
    return "Others/不明"

df["_db"] = [
    classify_db(u, d, p)
    for u, d, p in zip(url_col_val, doi_col_val, pub_col_val)
]

DB_ORDER = ["ACM", "IEEE", "Scopus/Elsevier", "PubMed/PsycInfo", "Others/不明"]
db_counts = df["_db"].value_counts()

print(f"  判定列: URL='{URL_COL}', DOI='{DOI_COL}', Publisher='{PUB_COL}'")
print()
print(f"  {'データベース':<22} {'件数':>8} {'割合':>8}")
print(f"  {'-'*22} {'-'*8} {'-'*8}")
for db in DB_ORDER:
    cnt = int(db_counts.get(db, 0))
    pct = cnt / TOTAL * 100
    print(f"  {db:<22} {cnt:>8,}  {pct:>7.1f}%")
print(f"  {'─'*22} {'─'*8} {'─'*8}")
print(f"  {'合計':<22} {TOTAL:>8,}  {'100.0%':>8}")

# Others の内訳（診断用）
others_mask = df["_db"] == "Others/不明"
if others_mask.sum() > 0:
    print()
    print("  -- Others/不明 の内訳 (DOIプレフィックス上位10件) --")
    doi_prefix = doi_col_val[others_mask].apply(
        lambda x: x[:7] if len(x) >= 7 else (x if x else "(DOI無し)")
    )
    top_doi = doi_prefix.value_counts().head(10)
    for prefix, cnt in top_doi.items():
        print(f"    DOI prefix '{prefix}' : {int(cnt):,} 件")

    print()
    print("  -- Others/不明 のURLドメイン上位10件 --")
    def extract_domain(url):
        m = re.search(r"https?://([^/]+)", url)
        return m.group(1) if m else ("(URL無し)" if url == "" else url[:40])
    others_domains = url_col_val[others_mask].apply(extract_domain)
    top_domains = others_domains.value_counts().head(10)
    for dom, cnt in top_domains.items():
        print(f"    {dom:<45} : {int(cnt):,} 件")

print()
print("=" * 70)
print("  集計完了 (データへの変更・ファイル出力なし)")
print("=" * 70)
