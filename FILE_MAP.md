# ファイルマップ — どこに何があるか

最終更新: 2026-10-15。リポジトリ直下の整理(`data/`・`legacy/` への移動)後の配置を、実ファイルを見て書いた。
プロトコル本文は `docs/protocol/rule.md`、実装の詳細は `README.md`、進捗は `docs/log/PROGRESS_LOG.md`。
このファイルは「場所の索引」で、手順や数値の正は上記の各文書にある。

行数・件数は 2026-10-15 に CSV を実際に数えた値(ヘッダ行を除く)。

## まずここを見る

| 知りたいこと | 見る場所 |
|---|---|
| 研究の目的・RQ・PICOS・分類体系 | `docs/protocol/rule.md` |
| プロトコルの変更履歴(Rev.N) | `docs/log/protocol_changelog.md` |
| 今どこまで進んでいるか | `docs/log/PROGRESS_LOG.md` |
| 判定シートの運用・κ・協議 | `screening/README.md`、`docs/protocol/screening_protocol.md` |
| 最終判定(Phase 4 へ進む論文) | `screening/final/final_decisions.csv` |
| Phase 4 の全文 PDF の取得状況 | `fulltext/manifest.csv`、`fulltext/manual_fetch.md` |
| 検索式・検索の再現手順 | `docs/protocol/search_strings.md`、`docs/protocol/search_replication.md` |
| 文書間の不整合と決定ログ | `docs/log/consistency_audit_log.md` |

## トップレベル

| パス | 内容 |
|---|---|
| `README.md` | 実装ドキュメント(パイプラインの実行手順、数値、ディレクトリ構成) |
| `FILE_MAP.md` | このファイル |
| `pipeline.py` | メインパイプライン(Phase 1〜3a)。既定の入力は `data/merged/ResearchVR2.csv`、出力は `data/pipeline/`。**公式 step ファイルは凍結中。再実行しない** |
| `data/` | 入力・参照表・パイプライン出力 |
| `raw/` | DB 別のエクスポート原本(PRISMA 上段の根拠) |
| `docs/` | 全文書。`protocol/`(ルール)、`log/`(時系列の記録)、`reference/`(分析・検討・配布物)の3分類 |
| `screening/` | Phase 3b の判定シート一式と集計結果 |
| `fulltext/` | Phase 4 の全文 PDF と取得状況 |
| `scripts/` | 検証・監査・API 連携・判定シート生成のスクリプト |
| `outputs/` | スクリプトの出力(監査 CSV・実行ログ) |
| `legacy/` | 現行フローでは使わない初期プロトタイプ |
| `.claude/skills/` | このリポジトリ用のスキル(`survey-resume` / `survey-log` / `survey-pipeline` / `survey-pr`) |
| `.env` / `.env.example` | API キー(`.env` は git 管理外)/ 変数名のテンプレート |

## `data/` — 入力・参照表・パイプライン出力

### `data/merged/` 統合生データ
| ファイル | 件数 | 内容 |
|---|---|---|
| `ResearchVR2.csv` | 14,385 | 旧統合エクスポート(〜2026-05-15)。`pipeline.py` の既定入力。経緯として保存 |
| `ResearchVR3.csv` | 14,682 | 第1波 4DB + IEEE 更新分。旧入力 |
| `ResearchVR4.csv` | 26,434 | **現行入力**。3DB × 第1波+第2波、`Source_DB` 列つき(`scripts/merge_raw.py` で生成) |

### `data/reference/` 参照表
| ファイル | 内容 |
|---|---|
| `CORE.csv` | CORE 学会ランキング(ヘッダなし。ファイル 987 行 / `pipeline.py` が読み込む正規化キーのエントリ数は 1,956) |
| `scimagojr 2025.csv` | SJR ジャーナルランキング(セミコロン区切り。ファイル 32,193 行 / 読み込み後のエントリ数は 50,327) |
| `venue_aliases.csv` | 著者確認済みの Venue エイリアス表(445 行)。Phase 2 の最優先照合 |
| `self_scale_references.csv` | 正式 gold set(25 行)。`SearchScope` 列で in-scope / background を区別。Known-Item Test の基準 |

### `data/pipeline/` `pipeline.py` の出力(公式 step ファイル)
| ファイル | 件数 | 内容 |
|---|---|---|
| `step1_dedup.csv` | 18,342 | Phase 1: 重複削除後 |
| `step1_5_filter_included.csv` / `_excluded.csv` | 6,317 / 12,025 | Phase 1.5: フィルタ層の通過 / 除外 |
| `step2_rank_included.csv` / `_excluded.csv` | 1,179 / 5,138 | Phase 2: Venue ランクの通過 / 除外 |
| `step3_kw_included.csv` / `_excluded.csv` | 795 / 384 | Phase 3a: キーワード除外の通過(最終候補)/ 除外 |
| `pipeline_log.txt` | — | 実行ログ(詳細・最新値はここ) |

> 件数は `pipeline_log.txt` の最終実行値と一致する(6,317 − 1,179 = 5,138、1,179 − 795 = 384 とも整合する)。

## `raw/` DB 別エクスポート原本
| ファイル | 件数 | 内容 |
|---|---|---|
| `acm.csv` / `ieee.csv` / `Scopus.csv` / `PubMed.csv` | 7,997 / 1,276 / 4,331 / 781 | 第1波の DB 別エクスポート(PubMed は Rev.8 で不使用) |
| `IEEE_2025-2026.csv` | 297 | IEEE 更新検索分 |
| `acm_wave2_20260803.csv` / `ieee_wave2_20260810.csv` / `scopus_wave2_20260730.csv` | 9,630 / 361 / 2,542 | 第2波(Rev.6) |
| `*.bib` / `scopus_wave2_20260730.ris` / `acm2/` / `IEEE2/` | — | 分割エクスポートの中間物と API の生出力(`.bib` と `acm2/`・`IEEE2/` は git 管理外) |

## `docs/` 文書

### `docs/protocol/` ルールを定める文書(一次情報)
| ファイル | 内容 |
|---|---|
| `rule.md` | 研究プロトコル本体(目的・RQ・PICOS・Phase 3b/4・分類体系・κ 閾値方針・参考文献 §5) |
| `screening_protocol.md` | Phase 3b の運用手順 |
| `snowballing_protocol.md` | 引用探索の手続き |
| `search_strings.md` | DB 別検索式の記録(PRISMA Item #7) |
| `search_replication.md` | 検索記録の復元・再実行手順 |

### `docs/log/` 記録(時系列。過去分は遡及修正しない)
| ファイル | 内容 |
|---|---|
| `PROGRESS_LOG.md` | 進捗ログ(セッションごとに追記)。**パスの旧→新の対応表は 2026-10-15 の項** |
| `protocol_changelog.md` | プロトコル変更履歴(Rev.N)。CSUR の protocol deviations 報告に転用する |
| `consistency_audit_log.md` | 文書間の不整合と決定ログ |
| `consensus_meeting_2_blank24.md` | 協議 2 回目で最終判定が空欄だった 24 件の一覧 |
| `doc_audit_20261015.md` | 現行文書の精査（2026-10-15）の更新箇所・旧記載・根拠の一覧。更新箇所は元の記載を `<!-- … 旧: … -->` で残している <!-- [2026-10-15 追加] 旧: (記載なし) -->

### `docs/reference/` 分析・検討・配布物
| ファイル | 内容 |
|---|---|
| `methodology_rationale.md` | Phase 3b までの手法と意図・想定質問 |
| `methodology_decision_Rev7.md` | 検索方法論のデータ検証・確定(Rev.7/8) |
| `screening_method_alternatives.md` | 代替スクリーニング手法 10 件の比較検討 |
| `normalization_design.md` | Venue 正規化関数の見直し案(案 1〜6) |
| `known_items.md` / `known_item_analysis.md` | 既知文献リスト / Known-Item Test の自動生成レポート |
| `reviewer_briefing*.{md,tex,pdf}` | 評価者向け説明資料(詳細版 / 事前配布版)。`.aux` `.log` `.out` は LaTeX の中間物 |
| `screening_decision_card.md` | 判定中に手元に置く 1 枚(基準の写し。新しい基準は含まない) |
| `GradThesis_Maeno_2025.pdf` | 参考卒論(追跡対象。PDF の置き場はここ) |

## `screening/` Phase 3b の判定シートと集計

git 管理されているのは `README.md`、`stage1/assignment.csv`・`abstract_ja.json`・記入見本、`consensus/consensus_worklist.csv`、`final/final_decisions.csv`。
**評価者の判定シートは独立性を守るため `.gitignore` で追跡しない**(混入に注意)。

| パス | 内容 |
|---|---|
| `README.md` | 判定の運用・語彙・凍結の方針の正 |
| `stage1/assignment.csv` | 判定対象 1,052 件の割当(record_id・ブロック・校正セット・担当・DOI) |
| `stage1/EXAMPLE_記入見本.{csv,xlsx}` | 全員に配った記入例 |
| `stage1/abstract_ja.json`、`stage1/json/` | 要旨の和訳キャッシュと閲覧アプリ用データ |
| `consensus/consensus_worklist.csv` | 協議の対象(183 行)。会議の結果の転記先 |
| `final/final_decisions.csv` | 最終判定(343 行)。`score_screening.py` が生成 |

> **配置のずれに注意:** この作業コピーでは、評価者ごとの判定シート(`sheet_*.{csv,xlsx}`・`supplement_sheet_*`・
> `stage2_sheet_*`)と `consensus_meeting*.xlsx`、`review_author.html` が **`screening/` 直下**にあり、未追跡である。
> README と `.gitignore` が想定する `stage1/`・`stage2/`・`calibration_supplement/`・`consensus/` の下ではない。
> `screening/` は凍結中のため、移動はしていない。

## `fulltext/` Phase 4 の全文
| パス | 内容 |
|---|---|
| `manifest.csv` | 対象 169 件の取得状況・出所・担当ペア・DOI(git 管理) |
| `manual_fetch.md` | 自動取得できなかった論文の手動取得リスト(`fetch_fulltext.py` が自動生成。手で編集しない) |
| `pdf/<record_id>.pdf` | 全文 PDF の原本(git 管理外) |
| `by_reviewer/{author,kataoka,watanabe}/` | 担当者ごとのコピー(git 管理外) |
| `manual/` | ブラウザで手動取得した PDF の置き場(`sort_fulltext_inbox.py` で振り分け) |

## `scripts/` スクリプト一覧

Python の実行は `python -X utf8 scripts/<name>.py`。出力を上書きするものがあるので、実行前に docstring を読む。

### 検索・データ取り込み
| ファイル | 内容 |
|---|---|
| `api_search_common.py` | 検索 API の共通部品(クエリビルダー・RIS 出力・`.env` 読み込み) |
| `db_search_ieee.py` / `db_search_scopus.py` | IEEE Xplore / Scopus API による第 2 波検索 |
| `snowball_search.py` | Semantic Scholar API によるスノーボーリング |
| `merge_raw.py` / `merge_bib.py` | `raw/` から統合生データ(`ResearchVR4.csv`)を作る / 分割 `.bib` を統合 |
| `enrich_abstracts.py` / `enrich_screening_abstracts.py` | DOI から要旨を補完(全体 / 判定対象のみ) |
| `translate_abstracts.py` | 要旨の和訳キャッシュを作る |

### 監査・検証
| ファイル | 内容 |
|---|---|
| `raw_db_audit.py` / `export_completeness_audit.py` | DB 別生データの監査 / エクスポートの打ち切り検出 |
| `known_item_test.py` / `known_item_screening_audit.py` | Known-Item Test(recall 測定)/ 判定対象に残ったかの照合 |
| `venue_match_audit.py` / `venue_dropped_audit.py` / `unmatched_venue_audit.py` | Venue 照合の誤り・脱落・未照合の監査 |
| `normalization_collision_audit.py` / `pubmed_unique_audit.py` | 正規化の同名衝突検出 / PubMed 固有件数の監査 |
| `audit_manuscript_figures.py` | 原稿(`SelfScaleSurvey/main.tex`)の数値を実データと突合 |
| `simulate_screening.py` | 足切りシミュレーション・DB 集計(読み取り専用) |

### Phase 3b(判定シートと集計)
| ファイル | 内容 |
|---|---|
| `make_screening_sheets.py` / `make_screening_xlsx.py` | 判定シート(CSV / Excel)の生成。**`--force` は記入済みの判定を破棄する** |
| `make_screening_example.py` | 記入見本の生成 |
| `make_calibration_supplement.py` | 校正セット拡大分の補足シート |
| `make_screening_stage2.py` / `add_stage2_note.py` | stage 2 シートの生成 / 境界例メモシートの追加 |
| `make_consensus_sheet.py` | 協議ミーティング用シートの生成 |
| `make_review_app.py` / `apply_review_decisions.py` | 判定用のローカル閲覧アプリの生成 / その判定の反映 |
| `score_screening.py` | 集計(Cohen's κ・不一致抽出・`final_decisions.csv` の確定) |

### Phase 4(全文)
| ファイル | 内容 |
|---|---|
| `fetch_fulltext.py` | OpenAlex で OA の PDF を探して取得し、担当ペアごとのフォルダへ複製 |
| `sort_fulltext_inbox.py` | 手動取得した PDF を中身で照合して `record_id` に振り分け |

## `outputs/` スクリプトの出力
| ファイル | 出力元 |
|---|---|
| `api_search_log.csv` | `db_search_*.py` |
| `enriched_abstracts.csv`、`enrich_abstracts_report.csv` | `enrich_*abstracts.py`(補完した要旨のキャッシュと報告) |
| `export_completeness.csv` | `export_completeness_audit.py` |
| `raw_db_audit.csv`、`pubmed_unique_175.csv` | `raw_db_audit.py`、`pubmed_unique_audit.py` |
| `known_item_test.csv`、`known_item_in_screening.csv`、`venue_dropped_known_items.csv` | `known_item_test.py`、`known_item_screening_audit.py`、`venue_dropped_audit.py` |
| `venue_match_audit.csv`、`venue_suspect_matches.csv`、`unmatched_venues_top50.csv` | `venue_match_audit.py`、`unmatched_venue_audit.py` |
| `normalization_collisions.csv`、`collisions_rank_conflict.csv` | `normalization_collision_audit.py` |
| `snowballing_log.csv`、`snowballing_log_pre20260810.csv` | `snowball_search.py`(後者は Rev.10 改修前の旧 12 列版) |
| `sjr_q2_excluded_venues.csv` | `audit_manuscript_figures.py` が読む(Q2 で脱落した Venue) |

## `legacy/` 初期プロトタイプ(現行フローでは使わない)
`prisma_screening.py`(キーワード除外の単体版)、`venue_screening.py`(Venue ランクの試作)、
`year_distribution.py` と `.png`(1,784 件時点の年次分布の図)。

## 追跡しないもの(`.gitignore`)
`.env`、`raw/*.bib`・`raw/acm2/`・`raw/IEEE2/`、評価者の判定シート(`sheet_*`・`supplement_sheet_*`・`stage2_sheet_*`)、
協議シート、`fulltext/pdf/`・`fulltext/by_reviewer/`、`__pycache__/`。

## 別リポジトリ(同じ親フォルダ `SurveyPlot/` 内)
| フォルダ | 内容 |
|---|---|
| `../SelfScaleSurvey/` | 論文の原稿(`main.tex` ほか)。skills `/survey-paper`・`/paper-figures` もここ |
| `../docs-system/` | Semantic Scholar 文献ブラウザ(Next.js + Supabase + R2)。サーベイ本体とは未接続 |
| `../DocsSystem/` | 空の廃棄跡 |
