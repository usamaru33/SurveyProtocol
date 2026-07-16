---
name: survey-pipeline
description: サーベイのスクリーニングパイプライン（pipeline.py 等）の実行・改修をするときに使う。実行コマンド、入出力ファイル、注意点をまとめている。
---

# スクリーニングパイプラインの実行・改修

作業ディレクトリ: `SurveyProtocol/`

## コマンド（Windows では必ず `-X utf8` を付ける）

```bash
# Phase 1〜3 一括実行（入力: ResearchVR2.csv, CORE.csv, "scimagojr 2025.csv"）
python -X utf8 pipeline.py

# 足切りシミュレーション・DB集計（読み取り専用、ファイル出力なし）
python -X utf8 simulate_screening.py

# キーワード除外の単体実行（--dry-run でファイル出力なし）
python -X utf8 prisma_screening.py --input step2_rank_included.csv --outdir ./

# 年次分布の可視化 → year_distribution.png
python -X utf8 year_distribution.py

# Known-Item Test(known_items.md 記入後)→ outputs/known_item_test.csv + known_item_analysis.md
python -X utf8 scripts/known_item_test.py

# Venue未照合5,126件の監査 → outputs/unmatched_venues_top50.csv(数分かかる)
python -X utf8 scripts/unmatched_venue_audit.py
```

依存: `pandas`（可視化は `matplotlib` も）。

## データフロー

```
ResearchVR2.csv (14,385)
 → step1_dedup.csv (12,442)            # DOI→Key→Title の順で重複検出
 → step2_rank_included.csv (2,858)     # CORE A/A* または SJR Q1 のみ通過
 → step3_kw_included.csv (1,784) ★最終候補
   （除外側: step2_rank_excluded.csv / step3_kw_excluded.csv、ログ: pipeline_log.txt）
```

## 注意点

- 出力CSVは再実行で上書きされる。数値を README / PROGRESS_LOG に反映済みなので、**基準を変えて再実行したら必ず両方更新**する。
- CSVは Zotero エクスポート形式。**引用数列が無い**。Abstract 欠損が約31%ある。
- Venue照合は 正規化完全一致 → 小文字一致 → 括弧内頭字語 → ファジー(≥0.82, CORE限定) の順。Unmatched 5,126件は一括除外されている点に注意。
- rule.md の Phase 3（LLM要旨判定: HCI=再現率優先 / 心理=PICOS厳格）は未実装。実装する場合は step3_kw_included.csv を入力とし、既存の命名規則（stepN_*_included/excluded.csv）に合わせる。
- **再現性要件（ACM Computing Surveys 投稿前提）: 包含/除外の判定に AI/LLM を使わない。全基準は決定論的であること。** 検証スクリプト（scripts/）は pipeline.py の関数を import して基準の乖離を防いでいる — 照合ロジックを変えるときは pipeline.py 側を変更する。
