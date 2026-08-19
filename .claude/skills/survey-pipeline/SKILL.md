---
name: survey-pipeline
description: サーベイのスクリーニングパイプライン（pipeline.py 等）の実行・改修をするときに使う。実行コマンド、入出力ファイル、注意点をまとめている。
---

# スクリーニングパイプラインの実行・改修

作業ディレクトリ: `SurveyProtocol/`

> ## 🛑 現在パイプラインは凍結中（2026-08-19〜）
>
> **Phase 3b の判定シートを評価者へ配布済み。** 判定対象 1,052件・判定手法・シートの
> 構成は確定しており、**再実行も再生成も行ってはならない。**
>
> - `pipeline.py` を再実行すると step ファイルが上書きされ、配布済みシートと
>   対応が取れなくなる
> - `make_screening_xlsx.py --force` は**評価者の記入済み判定を破棄する**
> - 判定基準・除外理由の語彙・割当の変更は、配布後は**プロトコル違反**になる
>
> 凍結解除は著者の明示的な指示があるときだけ。判定が全員完了し `final_decisions.csv`
> が確定するまでは、このファイル群を読むことはあっても書いてはならない。
> 詳細は `docs/screening_protocol.md` と `screening/README.md` の凍結告知を参照。

## コマンド（Windows では必ず `-X utf8` を付ける）

```bash
# --- Phase 1〜3a 一括実行（★凍結中。実行しないこと） ---
python -X utf8 pipeline.py

# 足切りシミュレーション・DB集計（読み取り専用、ファイル出力なし）
python -X utf8 simulate_screening.py

# 年次分布の可視化 → year_distribution.png
python -X utf8 year_distribution.py

# Known-Item Test（known_items.md 記入後）→ outputs/known_item_test.csv
python -X utf8 scripts/known_item_test.py

# Venue 照合の監査（読み取り専用）
python -X utf8 scripts/venue_match_audit.py
python -X utf8 scripts/unmatched_venue_audit.py
```

依存: `pandas`（可視化は `matplotlib`、判定シートは `openpyxl`）。

## データフロー（現行確定値: 2026-08-12 実行, Rev.13）

```
ResearchVR4.csv (26,434)                # 3DB × 第1波+第2波、Source_DB 列つき
 → step1_dedup.csv (18,342)             # DOI→Key→Title の順で重複検出＋フィールドマージ
 → step1_5_filter_included.csv (6,317)  # フィルタ層: 正規化クエリを一律再適用
 → step2_rank_included.csv (1,179)      # CORE A/A* または SJR Q1 のみ通過
 → step3_kw_included.csv (795)          # キーワード除外（Phase 3a）
```

**Phase 3b の判定対象は 1,052件** = DB検索 795 + 引用探索（スノーボーリング）257。
引用探索分には venue フィルタ（Phase 2）とフィルタ層（Phase 1.5）を適用していない
（`docs/snowballing_protocol.md` §4.3b）。判定基準は両者で同一。

> **旧値（14,682→12,543→2,909→1,827、入力 ResearchVR3.csv）は第1波・4DB 前提であり
> 以後は使用しない。** さらに古い ResearchVR2.csv(14,385) 系も同様。

## Phase 3b（人手判定）の関連スクリプト

```bash
python -X utf8 scripts/make_screening_sheets.py      # 割当と雛形CSV（決定論的）
python -X utf8 scripts/make_screening_xlsx.py        # 評価者が記入する xlsx
python -X utf8 scripts/make_screening_example.py     # 記入見本
python -X utf8 scripts/make_screening_stage2.py      # stage 2（著者の stage 1 完了後）
python -X utf8 scripts/score_screening.py            # 集計・κ・理由別内訳
```

**上記はいずれも凍結中。** `score_screening.py` だけは読み取りと集計のみなので、
記入状況の確認に使ってよい（`final_decisions.csv` の生成は未解決がゼロのときのみ）。

## 注意点

- 出力CSVは再実行で上書きされる。数値を `README.md` / `docs/PROGRESS_LOG.md` に
  反映済みなので、**基準を変えて再実行したら必ず両方更新**する。
- Venue照合は 正規化完全一致 → 小文字一致 → 括弧内頭字語 → ファジー(≥0.82, CORE限定) の順。
  Rev.12 で種別マーカー・短キーガードを追加済み。unmatched は一括除外される点に注意。
- 除外理由の統制語彙（Rev.18）の**正は `scripts/make_screening_xlsx.py` の
  `EXCLUDE_REASONS`**。文書側は写しなので手で直さない。
- 方法論上の主張の**出典は `docs/rule.md` §5 に集約**する。他文書は `[R1]` 等で参照する。
- **再現性要件（ACM Computing Surveys 投稿前提）: 包含/除外の判定に AI/LLM を使わない
  （`rule.md` Rev.2）。全基準は決定論的であること。** Phase 3b は人手2〜3名の
  liberal accelerated で行う。検証スクリプト（`scripts/`）は `pipeline.py` の関数を
  import して基準の乖離を防いでいる — 照合ロジックを変えるときは `pipeline.py` 側を変更する。
- PR を作るときは `/survey-pr` を通す（全文書への反映漏れを検証する手順）。
