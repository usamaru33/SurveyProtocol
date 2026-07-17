#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
known_item_test.py — Known-Item Test(検索戦略・スクリーニング基準の妥当性検証)
================================================================================

【何を】
著者が事前に「必ず含まれるべき」と判断した既知文献(known_items.md の
quasi-gold standard セット)が、スクリーニングパイプラインの各段階で
生存しているかを決定論的に検証する。LLM/AI 判定は一切使わない。

【なぜ】
ACM Computing Surveys 投稿要件として、検索式の再現率(recall)と
スクリーニング基準の妥当性を Known-Item Test(quasi-gold standard;
cf. Kitchenham & Charters 2007)で示すため。段階別の脱落理由を特定し、
検索式の欠陥 / Venueホワイトリストの欠陥 / 除外キーワードの過剰を切り分ける。

【入力】
  - 既知文献リスト(--items で指定。省略時は known_items.csv → known_items.md →
    self_scale_references.csv の順に探す)。列名は柔軟に解決する
    (DOI_or_URL / ID / Section / Role_in_Survey 等のエイリアス対応)
  - ResearchVR*.csv           step0: 統合生データ(最新版 = 名前の昇順で最後を自動選択)
  - step1_dedup.csv           step1: 重複削除後 12,442件
  - step2_rank_included.csv   step2: Venueランク通過 2,858件
  - step2_rank_excluded.csv   step2 脱落理由の特定用(Excl_Reason_Phase2)
  - step3_kw_included.csv     step3: キーワード除外後 1,784件(最終候補)
  - step3_kw_excluded.csv     step3 脱落理由の特定用(KW_Excl_Category/Keywords)
  - CORE.csv / scimagojr 2025.csv  step2脱落Venueのランク調査用

【出力】
  - outputs/known_item_test.csv   既知文献 × 各step の生存フラグ・照合方法・脱落理由
  - known_item_analysis.md        脱落分析レポート(自動生成、証拠つき)
  - 標準出力                       段階別 recall サマリ

【照合規則(決定論的)】
  1. DOI 完全一致(小文字化、https://doi.org/ 等のプレフィックス除去)
  2. 正規化タイトル完全一致(小文字化・英数字以外を空白化・空白正規化)
  3. Levenshtein 類似度 ≥ 0.9 の候補を「FUZZY(要手動確認)」として提示するのみ。
     曖昧マッチを自動で生存扱いにはしない(recall には数えない)。

【step0 の判定単位】
  step0 は「統合生データ ResearchVR2.csv に存在するか」の判定。
  raw/*.csv(ZoteroのDB別コレクションエクスポート、2026-07-17 追加)が存在する場合は、
  どのDBコレクションに含まれるかを step0_source_dbs 列に併記する
  (= どのDBの検索式がその文献を捕捉したかまで特定できる)。
  raw/ が無い環境では URL/DOI プレフィックスからの出版社推定(source_db_guess)のみとなる。

実行: python -X utf8 scripts/known_item_test.py
"""

from __future__ import annotations

import csv
import re
import sys
from datetime import date
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent  # SurveyProtocol/
sys.path.insert(0, str(ROOT))

# 本番パイプラインと同一の照合基準を保証するため pipeline.py から直接 import する
from pipeline import (  # noqa: E402
    EXCLUSION_CATEGORIES,
    compile_exclusions,
    load_core,
    load_sjr,
    normalize_venue,
    screen_keywords,
)

FUZZY_THRESHOLD = 0.90  # Levenshtein 類似度の下限(候補提示用)

# 実際に実行された統合検索クエリ(search_strings.md / rule.md Rev.5)の3コンセプト群。
# step0 脱落分析に使用。※旧版はrule.md計画段階のクエリを使っていたが、実行版に訂正済み。
QUERY_CONCEPT_GROUPS: list[tuple[str, list[str]]] = [
    ("G1 没入環境", [r"\bvirtual reality\b", r"\bvr\b", r"\bhmd\b"]),
    ("G2 身体表象", [r"\bavatar[s]?\b", r"\bbod(?:y|ies)\b", r"\bembodiment\b"]),
    ("G3 スケール知覚", [r"\bsizes?\b", r"\bscales?\b", r"\bheights?\b",
                        r"\bdistances?\b"]),
]

TITLE_STOPWORDS = {
    "a", "an", "the", "of", "in", "on", "for", "with", "and", "or", "to",
    "is", "are", "does", "do", "how", "what", "when", "its", "their",
    "using", "via", "by", "from", "at", "as", "into", "through", "effect",
    "effects", "study", "toward", "towards",
}

def _latest_merged_name() -> str:
    """統合生データの最新版(ResearchVR2.csv, ResearchVR3.csv, ... の名前順で最後)。"""
    cands = sorted(p.name for p in ROOT.glob("ResearchVR*.csv"))
    if not cands:
        sys.exit("[ERROR] ResearchVR*.csv が見つかりません")
    return cands[-1]


STEPS = [
    ("step0", _latest_merged_name(), "統合生データ(検索式で拾えたか)"),
    ("step1", "step1_dedup.csv", "重複削除後"),
    ("step2", "step2_rank_included.csv", "Venueランク通過後"),
    ("step3", "step3_kw_included.csv", "キーワード除外通過後(最終候補)"),
]


# ---------------------------------------------------------------------------
# 正規化・照合ヘルパ
# ---------------------------------------------------------------------------

def norm_doi(raw: str) -> str:
    d = (raw or "").strip().lower()
    d = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    return d


def norm_title(raw: str) -> str:
    t = (raw or "").lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def levenshtein_within(a: str, b: str, k: int) -> int | None:
    """バンド幅 k の Levenshtein 距離。距離 > k なら None(枝刈り)。"""
    if abs(len(a) - len(b)) > k:
        return None
    if a == b:
        return 0
    la, lb = len(a), len(b)
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [k + 1] * lb
        lo, hi = max(1, i - k), min(lb, i + k)
        for j in range(lo, hi + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        if min(cur[lo:hi + 1]) > k:
            return None
        prev = cur
    return prev[lb] if prev[lb] <= k else None


def lev_similarity(a: str, b: str, floor: float = FUZZY_THRESHOLD) -> float | None:
    """Levenshtein 類似度 (1 - dist/max_len)。floor 未満なら None。"""
    m = max(len(a), len(b))
    if m == 0:
        return None
    k = int(m * (1 - floor))
    d = levenshtein_within(a, b, k)
    return None if d is None else 1 - d / m


def guess_source_db(url: str, doi: str) -> str:
    """URL/DOI プレフィックスから取得元DBを推定(simulate_screening.py と同基準)。"""
    url, doi = (url or "").lower(), (doi or "").lower()
    if "dl.acm.org" in url or doi.startswith("10.1145"):
        return "ACM"
    if "ieeexplore.ieee.org" in url or doi.startswith("10.1109"):
        return "IEEE"
    if "scopus.com" in url or "sciencedirect.com" in url or doi.startswith("10.1016"):
        return "Scopus/Elsevier"
    if "pubmed.ncbi.nlm.nih.gov" in url or doi.startswith("10.1037"):
        return "PubMed/PsycInfo"
    return "Others/Unknown"


# ---------------------------------------------------------------------------
# データ読み込み
# ---------------------------------------------------------------------------

class Dataset:
    """CSV 1本ぶんの照合インデックス(DOI 辞書 / 正規化タイトル辞書)。"""

    def __init__(self, path: Path):
        self.path = path
        self.rows: list[dict] = []
        self.by_doi: dict[str, dict] = {}
        self.by_title: dict[str, dict] = {}
        with path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
            for row in csv.DictReader(f):
                self.rows.append(row)
                d = norm_doi(row.get("DOI", ""))
                t = norm_title(row.get("Title", ""))
                if d and d not in self.by_doi:
                    self.by_doi[d] = row
                if t and t not in self.by_title:
                    self.by_title[t] = row

    def match(self, doi: str, title_n: str):
        """(row, method) を返す。確定一致しなければ (None, 'NONE')。"""
        if doi and doi in self.by_doi:
            return self.by_doi[doi], "DOI"
        if title_n and title_n in self.by_title:
            return self.by_title[title_n], "TITLE"
        return None, "NONE"

    def fuzzy_candidates(self, title_n: str, limit: int = 3) -> list[tuple[str, float]]:
        """Levenshtein 類似度 ≥ 閾値のタイトル候補(提示のみ、自動確定しない)。"""
        cands = []
        for t in self.by_title:
            s = lev_similarity(title_n, t)
            if s is not None:
                cands.append((t, s))
        cands.sort(key=lambda x: -x[1])
        return cands[:limit]


# 既知文献リストの列名エイリアス(canonical名 → 受理する列名の優先順)
ITEM_COL_ALIASES: dict[str, list[str]] = {
    "#": ["#", "ID", "No", "no"],
    "Title": ["Title", "title"],
    "Authors": ["Authors", "Author"],
    "Year": ["Year", "Publication Year"],
    "Venue": ["Venue", "Publication Title"],
    "DOI": ["DOI", "DOI_or_URL", "doi"],
    "Role": ["Role", "Role (Intro/RW/Taxonomy)", "Section"],
    "Rationale": ["Rationale", "Role_in_Survey"],
    "VenueType": ["VenueType"],
    "Priority": ["Priority"],
    "SearchScope": ["SearchScope", "Scope"],
}


def _canonicalize(row: dict) -> dict:
    out = {}
    for canon, aliases in ITEM_COL_ALIASES.items():
        for a in aliases:
            if a in row and (row.get(a) or "").strip():
                out[canon] = row[a].strip()
                break
        else:
            out[canon] = ""
    # DOI_or_URL 等に URL が入っている場合、文字列中の DOI(10.xxxx/...)を抽出
    if out["DOI"] and not out["DOI"].startswith("10."):
        m = re.search(r"\b10\.\d{4,9}/\S+", out["DOI"])
        out["DOI"] = m.group(0) if m else out["DOI"]
    return out


def parse_known_items(root: Path, items_path: Path | None = None) -> list[dict]:
    """既知文献リストを読む。--items 指定 > known_items.csv > known_items.md >
    self_scale_references.csv の順。列名はエイリアス解決する。"""
    if items_path is None:
        for cand in ("known_items.csv", "known_items.md",
                     "self_scale_references.csv"):
            p = root / cand
            if p.exists():
                if cand == "known_items.md":
                    # md はテンプレートのみ(有効行なし)の場合があるため中身で判断
                    md_items = _parse_md_table(p)
                    if md_items:
                        return md_items
                    continue
                items_path = p
                break
        else:
            sys.exit("[ERROR] 既知文献リストが見つかりません(--items で指定可)")
    if items_path is None:
        return []
    if items_path.suffix.lower() == ".md":
        return _parse_md_table(items_path)
    with items_path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        items = [_canonicalize(r) for r in csv.DictReader(f)]
    print(f"[INFO] 既知文献リスト: {items_path.name}")
    return _valid_only(items)


def _parse_md_table(md_path: Path) -> list[dict]:
    items = []
    header: list[str] | None = None
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            if cells and cells[0] in ("#", "No", "no", "ID"):
                header = ["#", "Title", "Authors", "Year", "Venue", "DOI",
                          "Role", "Rationale"]
            continue
        if set("".join(cells)) <= set("-: "):
            continue  # 区切り行
        row = dict(zip(header, cells + [""] * (len(header) - len(cells))))
        items.append(_canonicalize(row))
    return _valid_only(items)


def _valid_only(items: list[dict]) -> list[dict]:
    return [it for it in items
            if (it.get("Title") or "").strip()
            and not (it.get("Title") or "").strip().upper().startswith("EXAMPLE:")]


# ---------------------------------------------------------------------------
# 脱落理由の特定
# ---------------------------------------------------------------------------

def phase2_drop_reason(row_excl: dict) -> str:
    reason = (row_excl.get("Excl_Reason_Phase2") or "").strip()
    venue = (row_excl.get("Publication Title") or "").strip() or "(空欄)"
    if reason.startswith("Venue not found"):
        return f"Venue名 '{venue}' が CORE/SJR いずれにも未照合"
    if reason.startswith("SJR"):
        q = (row_excl.get("SJR_Quartile") or "?").strip()
        mv = (row_excl.get("Matched_Venue") or "").strip()
        return f"SJR '{q}' のため除外 (venue: '{venue}' → 照合先: '{mv}')"
    if reason.startswith("CORE"):
        r = (row_excl.get("CORE_Rank") or "?").strip()
        mv = (row_excl.get("Matched_Venue") or "").strip()
        return f"CORE Rank '{r}' (< A) のため除外 (venue: '{venue}' → 照合先: '{mv}')"
    return reason or "理由不明(除外CSVに理由列なし)"


def phase3_drop_reason(row_excl: dict) -> str:
    cat = (row_excl.get("KW_Excl_Category") or "").strip()
    kws = (row_excl.get("KW_Excl_Keywords") or "").strip()
    return f"除外キーワード命中: [{cat}] {kws}"


def concept_group_hits(text: str) -> dict[str, list[str]]:
    """統合検索クエリの各コンセプト群について、text に命中した語を返す。"""
    hits: dict[str, list[str]] = {}
    low = (text or "").lower()
    for label, pats in QUERY_CONCEPT_GROUPS:
        hits[label] = [p for p in pats if re.search(p, low)]
    return hits


def title_candidate_terms(title: str) -> list[str]:
    """step0 脱落時の検索式拡張候補: タイトル中の内容語(ストップワード除去)。"""
    words = re.findall(r"[a-z][a-z\-]{2,}", (title or "").lower())
    return [w for w in words if w not in TITLE_STOPWORDS]


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="Known-Item Test")
    ap.add_argument("--items", type=Path, default=None,
                    help="既知文献リストのパス(省略時は自動探索)")
    args = ap.parse_args()
    items = parse_known_items(ROOT, args.items)
    outdir = ROOT / "outputs"
    outdir.mkdir(exist_ok=True)
    out_csv = outdir / "known_item_test.csv"
    out_md = ROOT / "known_item_analysis.md"

    if not items:
        msg = ("known_items.md がまだ記入されていません(有効行 0 件)。"
               "記入後に再実行してください。")
        print(f"[INFO] {msg}")
        out_md.write_text(
            f"# Known-Item 脱落分析レポート\n\n> 自動生成: {date.today()} — {msg}\n",
            encoding="utf-8")
        return

    # SearchScope='background'(書籍・非VRの理論/心理研究)は検索で拾えなくて正常なため、
    # recall の分母から除外する(存在チェック自体は行わず、レポートに件数のみ記す)
    background = [it for it in items
                  if (it.get("SearchScope") or "").lower() == "background"]
    items = [it for it in items
             if (it.get("SearchScope") or "").lower() != "background"]
    if background:
        print(f"[INFO] SearchScope=background の {len(background)} 件は recall 計算から除外"
              "(手動追加すべき背景文献): "
              + "; ".join((it.get("Title") or "")[:40] for it in background))

    print(f"[INFO] Known items(in-scope): {len(items)} 件(目標 15〜25 件、最低 10 件推奨)")
    if len(items) < 10:
        print("[WARN] 10 件未満です。quasi-gold standard としては不足(Kitchenham 推奨最低 10 件)。")

    datasets = {key: Dataset(ROOT / fname) for key, fname, _ in STEPS}
    excl2 = Dataset(ROOT / "step2_rank_excluded.csv")
    excl3 = Dataset(ROOT / "step3_kw_excluded.csv")
    # DB別コレクション(あれば): どのDBの検索式が捕捉したかの特定用
    raw_datasets = {p.stem: Dataset(p) for p in sorted((ROOT / "raw").glob("*.csv"))}
    if raw_datasets:
        print(f"[INFO] DB別生データ: {', '.join(raw_datasets)} を照合に使用")
    compiled_excl = compile_exclusions(EXCLUSION_CATEGORIES)

    results: list[dict] = []
    for it in items:
        doi = norm_doi(it.get("DOI", ""))
        title_n = norm_title(it.get("Title", ""))
        rec: dict = {
            "#": it.get("#", ""),
            "Title": it.get("Title", "").strip(),
            "DOI": doi,
            "Year": it.get("Year", "").strip(),
            "Venue_expected": it.get("Venue", "").strip(),
            "Role": it.get("Role", "").strip(),
            "VenueType": it.get("VenueType", "").strip(),
        }
        drop_stage, drop_reason = "", ""
        matched_row_step0 = None
        for key, _, _ in STEPS:
            ds = datasets[key]
            row, method = ds.match(doi, title_n)
            rec[f"{key}_survived"] = "Y" if row is not None else "N"
            rec[f"{key}_match_method"] = method
            if row is not None:
                if key == "step0":
                    matched_row_step0 = row
                continue
            # 未確定 → FUZZY 候補提示(自動確定しない)
            cands = ds.fuzzy_candidates(title_n)
            if cands:
                rec[f"{key}_match_method"] = "FUZZY(要手動確認)"
                rec[f"{key}_fuzzy_candidates"] = " || ".join(
                    f"{t} (lev={s:.3f})" for t, s in cands)
            if not drop_stage:
                drop_stage = key
                if key == "step0":
                    drop_reason = "統合生データに不在 = 検索式で拾えていない"
                elif key == "step1":
                    drop_reason = ("重複削除後に不在(正本にも不一致)。"
                                   "DOI/タイトル表記の確認が必要")
                elif key == "step2":
                    r, _ = excl2.match(doi, title_n)
                    drop_reason = phase2_drop_reason(r) if r else \
                        "step2 除外CSVにも不在(照合キー要確認)"
                elif key == "step3":
                    r, _ = excl3.match(doi, title_n)
                    drop_reason = phase3_drop_reason(r) if r else \
                        "step3 除外CSVにも不在(照合キー要確認)"
        rec["drop_stage"] = drop_stage or "(全段階生存)"
        rec["drop_reason"] = drop_reason
        if matched_row_step0 is not None:
            rec["source_db_guess"] = guess_source_db(
                matched_row_step0.get("Url", ""), matched_row_step0.get("DOI", ""))
        else:
            rec["source_db_guess"] = ""
        rec["step0_source_dbs"] = "; ".join(
            db for db, ds in raw_datasets.items()
            if ds.match(doi, title_n)[0] is not None)
        results.append(rec)

    # ---- outputs/known_item_test.csv ----
    fieldnames = ["#", "Title", "DOI", "Year", "Venue_expected", "Role",
                  "VenueType", "source_db_guess", "step0_source_dbs"]
    for key, _, _ in STEPS:
        fieldnames += [f"{key}_survived", f"{key}_match_method",
                       f"{key}_fuzzy_candidates"]
    fieldnames += ["drop_stage", "drop_reason"]
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for rec in results:
            w.writerow(rec)

    # ---- recall サマリ(標準出力) ----
    n = len(results)
    print()
    print("=" * 64)
    print("  Known-Item Test — 段階別 recall")
    print("=" * 64)
    for key, fname, desc in STEPS:
        surv = sum(1 for r in results if r[f"{key}_survived"] == "Y")
        fuzzy = sum(1 for r in results
                    if r[f"{key}_survived"] == "N"
                    and r[f"{key}_match_method"].startswith("FUZZY"))
        note = f"  (+FUZZY要確認 {fuzzy})" if fuzzy else ""
        print(f"  {key} {desc:<24}: {surv:>3}/{n}  recall={surv / n:.2%}{note}")
    print()
    for r in results:
        if r["drop_stage"] != "(全段階生存)":
            print(f"  [DROP@{r['drop_stage']}] {r['Title'][:60]}")
            print(f"      → {r['drop_reason']}")
    print(f"\n  出力: {out_csv}")

    # ---- known_item_analysis.md(Task 3 レポート) ----
    write_analysis_md(out_md, results, n, datasets)
    print(f"  出力: {out_md}")


def write_analysis_md(out_md: Path, results: list[dict], n: int, datasets) -> None:
    """脱落分析レポートを生成する。段階ごとに証拠と決定論的な改善提案を付す。"""
    core = load_core(ROOT / "CORE.csv")
    sjr = load_sjr(ROOT / "scimagojr 2025.csv")

    lines = [
        "# Known-Item 脱落分析レポート",
        "",
        f"> `scripts/known_item_test.py` による自動生成({date.today()})。",
        f"> Known-Item {n} 件。判定は全て決定論的(DOI/正規化タイトル一致)。",
        "> FUZZY 候補は手動確認が必要であり、recall には算入していない。",
        "",
        "## 段階別 recall",
        "",
        "| 段階 | 内容 | 生存 | recall |",
        "|---|---|---|---|",
    ]
    for key, _, desc in STEPS:
        surv = sum(1 for r in results if r[f"{key}_survived"] == "Y")
        lines.append(f"| {key} | {desc} | {surv}/{n} | {surv / n:.1%} |")
    lines.append("")

    drops0 = [r for r in results if r["drop_stage"] == "step0"]
    drops2 = [r for r in results if r["drop_stage"] == "step2"]
    drops3 = [r for r in results if r["drop_stage"] == "step3"]
    drops_other = [r for r in results if r["drop_stage"] not in
                   ("(全段階生存)", "step0", "step2", "step3")]

    # ---- step0: 検索式の欠陥 ----
    lines += ["## step0 脱落 — 検索式の欠陥", ""]
    if not drops0:
        lines.append("該当なし(全 Known-Item が検索式で捕捉されている)。")
    for r in drops0:
        hits = concept_group_hits(r["Title"])
        missing = [g for g, h in hits.items() if not h]
        matched = {g: h for g, h in hits.items() if h}
        lines += [
            f"### {r['Title']}",
            "",
            f"- DOI: `{r['DOI'] or '(なし)'}` / 想定Venue: {r['Venue_expected']}",
        ]
        vt = (r.get("VenueType") or "").lower()
        if vt and vt not in ("conference", "journal"):
            lines.append(
                f"- **注: VenueType = {r['VenueType']}。書籍・章などは対象DBの検索範囲外の"
                "可能性が高く、検索式の欠陥とは限らない(背景文献として手動追加が妥当)。**")
        lines.append("- タイトルに対する検索クエリ・コンセプト群の命中状況:")
        for g, h in matched.items():
            lines.append(f"  - {g}: ✅ {', '.join(f'`{p}`' for p in h)}")
        for g in missing:
            lines.append(f"  - {g}: ❌ 命中なし ← **検索式が取りこぼす原因(の候補)**")
        cand = title_candidate_terms(r["Title"])
        lines += [
            f"- タイトル中の内容語(キーワード追加候補の母集団): {', '.join(f'`{w}`' for w in cand)}",
            "- 提案: 上記 ❌ のコンセプト群に、この論文で使われている同義語を OR 追加して"
            "再検索し、ヒット件数の増分を確認する。",
            "- 注: 実際の検索は Title+Abstract 対象のため、Abstract に命中語がある可能性"
            "もある。原文 Abstract を確認のうえ判断すること。",
            "",
        ]

    # ---- step1 など想定外の脱落 ----
    if drops_other:
        lines += ["## step1 等での想定外の脱落", ""]
        for r in drops_other:
            lines.append(f"- **{r['Title']}** — {r['drop_reason']}")
        lines.append("")

    # ---- step2: Venue ホワイトリストの欠陥 ----
    lines += ["## step2 脱落 — Venue ホワイトリストの欠陥", ""]
    if not drops2:
        lines.append("該当なし。")
    for r in drops2:
        lines += [f"### {r['Title']}", "", f"- 脱落理由: {r['drop_reason']}"]
        venue = r["Venue_expected"]
        norm = normalize_venue(venue)
        if venue:
            # CORE / SJR での最近傍を提示(表記ゆれ or ランク不足の切り分け)
            best = []
            for k, e in core.items():
                s = lev_similarity(norm, k, floor=0.75)
                if s is not None:
                    best.append((s, e["original_title"], f"CORE {e['rank']}"))
            for k, e in sjr.items():
                if k == "__issn_index__":
                    continue
                s = lev_similarity(norm, k, floor=0.85)
                if s is not None:
                    best.append((s, e["original_title"], f"SJR {e['quartile']}"))
            best.sort(key=lambda x: -x[0])
            if best:
                lines.append("- ランキングリスト内の最近傍(表記ゆれ調査):")
                for s, t, rk in best[:3]:
                    lines.append(f"  - `{t}` [{rk}] (lev={s:.3f})")
            else:
                lines.append("- ランキングリスト内に類似Venueなし(CORE lev≥0.75 / "
                             "SJR lev≥0.85 の範囲で候補ゼロ)。"
                             "`outputs/unmatched_venues_top50.csv` も参照。")
        if "SJR 'Q2'" in r["drop_reason"]:
            lines.append(
                "- 注記: SJR Q2 による除外。採用基準は「Q1のみ」で確定済み"
                "(protocol_changelog.md Rev.4)であり、この脱落は**基準どおりの動作**。"
                " Threats to Validity 節で報告する事例として記録する。")
        elif "未照合" in r["drop_reason"]:
            lines.append(
                "- 注記: ランク不足ではなく**照合漏れ**。類似Venueが提示されている場合は"
                "表記ゆれであり、正規化ルールまたはエイリアス表への追加で救済可能。"
                "類似Venueなしの場合は当該Venueがランキングリスト自体に未収載"
                "(ワークショップ等)であり、除外維持が妥当かを個別判断する。")
        lines.append("")

    # ---- step3: 除外キーワードの過剰 ----
    lines += ["## step3 脱落 — 除外キーワードの誤爆", ""]
    if not drops3:
        lines.append("該当なし。")
    for r in drops3:
        lines += [
            f"### {r['Title']}",
            "",
            f"- {r['drop_reason']}",
            "- 提案: 命中した正規表現の単語境界・文脈条件を厳格化するか、当該パターンを"
            "除外リストから外した場合の巻き添え件数(step3_kw_excluded.csv 内の同パターン"
            "命中数)を確認して判断する。",
            "",
        ]

    lines += [
        "---",
        "",
        "*本レポートは known_items.md 更新のたびに再生成される。手動の解釈・決定は "
        "PROGRESS_LOG.md に記録すること。*",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
