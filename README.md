# SurveyProtocol — VR自己スケール知覚 システマティック・レビュー

> **PRISMA 2020準拠**のスクリーニングパイプラインと集計ツールの実装ドキュメント。  
> VR空間における自己スケール感覚（Self-scale perception）の形成要因を網羅的に体系化するためのシステマティック・レビュープロジェクト。
>
> **現行の確定値 (2026-08-12 実行, Rev.13):** 入力 `ResearchVR4.csv`（26,434件 = 3DB × 第1波+第2波）
>
> ```
> 26,434 → 18,342（P1 重複削除）→ 6,317（P1.5 フィルタ層）→ 1,179（P2 Venue）→ 795（P3a キーワード）
> ```
>
> **⚠️ 本ドキュメントを読むときの前提（2026-08-12 時点）:**
> 1. **プロトコルは Rev.13 まで確定。`step*.csv` は Rev.13 で再実行済み**（2026-07-17 以来の凍結は解除）。
> 2. **§7 の追加分析の表は 2026-08-20 に現行データ（795件）で再実行済み**（旧版は 2026-05-25・1,784件時点だった）。
>    再実行が必要（§7 冒頭の注記参照）。
> 3. プロトコルの決定経緯・最新方針は `docs/log/protocol_changelog.md`（〜Rev.13）と
>    `docs/protocol/search_strings.md` が一次情報。本 README と食い違う場合は **docs/ 側が正**。

---

## 目次

1. [研究概要・目的](#1-研究概要目的)
2. [リサーチクエスチョン (RQ)](#2-リサーチクエスチョン-rq)
3. [スクリーニング戦略](#3-スクリーニング戦略)
4. [ファイル構成](#4-ファイル構成)
   - [データ取り込みの検証](#41-データ取り込みの検証2026-08-03-追加)
5. [パイプライン詳細](#5-パイプライン詳細)
   - [Phase 1: 重複削除](#phase-1-重複削除-pipeline.py)
   - [Phase 2: 学会ランクスクリーニング](#phase-2-学会ランクスクリーニング-pipeline.py)
   - [Phase 3: キーワード除外スクリーニング](#phase-3-キーワード除外スクリーニング-pipeline.py)
6. [スクリーニング実績（PRISMA数値）](#6-スクリーニング実績prisma数値)
   - [検索の網羅性検証（Known-Item Test）](#検索の網羅性検証known-item-test)
7. [追加分析ツール](#7-追加分析ツール)
   - [足切りシミュレーション](#タスク-1a-引用数による足切りシミュレーション)
   - [キーワードスコア分析](#タスク-1b-キーワードスコアによる足切りシミュレーション)
   - [取得元データベース集計](#タスク-2-取得元データベース集計)
8. [スノーボーリング（引用探索）](#8-スノーボーリング引用探索)
   - [Venueランクは採否に使わない](#85-venueランクの付与--採否には使わない)
   - [PRISMA 上の扱い](#87-prisma-上の扱い)
9. [分類体系 (Taxonomy)](#9-分類体系-taxonomy)
10. [実行方法](#10-実行方法)
11. [Phase 3b: 人手スクリーニングの実施](#11-phase-3b-人手スクリーニングの実施)
12. [期待される知見と貢献](#12-期待される知見と貢献)

---

## 1. 研究概要・目的

本システマティック・レビューの主たる目的は、**VR空間における自己スケール感覚（Self-scale perception）の形成に関わる諸要因を網羅的に体系化**し、現在の研究領域における「視覚情報の支配的影響」と「非視覚的情報の構造的欠落」を定量的な事実として提示することである。

具体的には、既存の実証研究を以下の三軸で構造化する:

- **介入モダリティ** — 何の感覚刺激を操作したか
- **評価対象（自己対環境）** — 身体スケール vs 外界スケールのどちらを評価したか
- **理論的枠組み** — ベイズ的最尤推定（MLE）の観点からどちらの情報が知覚を支配したか

最終目標は、身体運動に随伴する**聴覚・触覚フィードバック**（接地音・足裏振動等）が、自己スケールの確定および「身体化のもっともらしさ」を担保する上で果たす理論的役割を導出することである。

---

## 2. リサーチクエスチョン (RQ)

| RQ | 内容 |
|---|---|
| **RQ1** | 自己スケール感覚の形成において、これまでにどのような感覚モダリティが検討されてきたか？（視覚以外の非視覚的要因の定量的把握） |
| **RQ2** | 介入手法（独立変数）と評価指標（従属変数）の間にどのような構造的乖離が存在するか？（World-scale依存の評価系の問題） |
| **RQ3** | 研究は知覚の帰属について何を報告しているか？（第3軸で計数）そのうえで視覚単独のスケーリングの限界・錯誤とミニチュア効果等の境界条件を整理する |

旧 RQ4（多感覚統合モデルの理論的考察）は Rev.25 で RQ 一覧から外し、本レビューの理論的貢献として
原稿 §7 で提示する扱いに変更した。詳細は `docs/log/protocol_changelog.md` Rev.25。

---

## 3. スクリーニング戦略

### 検索対象データベース（Rev.8 で3DB体制に確定）

| データベース | 分野 | 採否 |
|---|---|---|
| ACM Digital Library | HCI・コンピュータサイエンス | ✅ 採用 |
| IEEE Xplore | 電気電子・HCI | ✅ 採用 |
| Scopus | 学際的（Elsevier系） | ✅ 採用 |
| ~~PubMed~~ | 医学・生命科学 | ❌ **Rev.8 で不使用に確定**（医学・治療目的の文献はスコープ外で主題適合性が低い）。初回検索は実施済み（781件、`raw/PubMed.csv`）だが **PRISMA報告からは除外** |
| ~~PsycInfo~~ | 心理学・認知科学 | ❌ **未実行**（アクセス制約）。心理系文献の捕捉は Scopus に依拠し、Known-Item Test で実証（#5/#6/#14 は Scopus 捕捉・#10 は Scopus 単独源） |

> 正当化ドラフト（Threats to Validity へ転用可）は `docs/reference/methodology_decision_Rev7.md` §Rev.8追記。

### 統合検索クエリ

**実際に実行されたクエリ（第1波、2026-07-17 著者確認により確定）:**

```
("Virtual Reality" OR "VR" OR "HMD")
AND ("Avatar" OR "Body" OR "Embodiment")
AND ("Size" OR "Scale" OR "Height" OR "Distance")
```

> ⚠️ rule.md 旧版・本README旧版に載っていた詳細クエリ（`"Virtual Environment"` `"Body ownership"`
> `"Size perception"` 等の複合語を含むもの）は**計画段階のものであり実行されていない**
> （`docs/log/protocol_changelog.md` Rev.5 で訂正）。

**Rev.6 改訂クエリ（第2波、G1のみ拡張。3DB分の再検索は完了 — ACM 9,630 / IEEE 361 / Scopus 2,542）:**

```
("Virtual Reality" OR "VR" OR "HMD" OR "head-mounted display"
 OR "head mounted display" OR "Virtual Environment*" OR "immersive virtual")
AND ("Avatar" OR "Body" OR "Embodiment")
AND ("Size" OR "Scale" OR "Height" OR "Distance")
```

G1 拡張の理由は Known-Item Test の脱落分析（Frontiers in Virtual Reality のDBカバレッジ欠落、
`"Virtual Environment"` 系の表記ゆれ取りこぼし）。DB別の verbatim 構文は
`scripts/api_search_common.py` の `CONCEPT_GROUPS_REV6` から機械生成し、手書きによる
DB間の表記不一致を防いでいる（§4・`docs/protocol/search_strings.md`）。

**検索対象フィールド: Title + Abstract（TA基準、Rev.7/8 で確定）**

| DB | 使用する構文 |
|---|---|
| Scopus | `TITLE-ABS(...)`（`TITLE-ABS-KEY` は索引語まで拾い scope が広がるため不可） |
| ACM | `Title:` / `Abstract:` を明示（`AllField:` は全文検索で過剰ヒット） |
| IEEE | `"Document Title":` / `"Abstract":`（`"All Metadata"` は不可） |

> **Threats to Validity に記載すべき既知の狭化:** 2026-07-27 の Scopus API 実測で
> `TITLE-ABS` = 2,533件 に対し `TITLE-ABS-KEY` = 4,727件。第1波の記録値（4,331件）は後者と整合するため、
> **第1波の Scopus は実際には TITLE-ABS-KEY で実行されていた可能性が高い**。
> 著者判断で TA基準は維持し、Keyword 経由でのみ捕捉されていた文献の残余リスクは
> スノーボーリング（§8）で緩和する。

### スクリーニング方針

**判定に AI/LLM は使用しない**（Rev.2 で全面廃止）。Phase 3 は決定論的キーワード除外、
Phase 4 は人手2名の二重スクリーニング（Cohen's κ で一致度を報告）。

| 分野 | 方針 |
|---|---|
| HCI（ACM / IEEE） | **保守的戦略（再現率優先）** ― 要旨にシステム提案しか書かれていなくても、スケール操作の記述があれば Included |
| 心理・学際（Scopus） | **PICOS厳格照合（適合率優先）** ― 生理的指標のみ・特定疾患患者対象の研究は高確度で除外 |

---

## 4. ファイル構成

```
SurveyProtocol/
├── ResearchVR2.csv              # 生データ（全DB統合エクスポート, 14,385件, 〜2026-05-15）
├── ResearchVR3.csv              # 旧入力（第1波4DB, 14,682件。経緯として保存）
├── ResearchVR4.csv              # ★ 現行入力（3DB × 第1波+第2波 = 26,434件、Source_DB列つき）
├── raw/                         # ZoteroのDB別コレクションエクスポート（PRISMA上段の根拠）
│   ├── acm.csv / ieee.csv / IEEE_2025-2026.csv / PubMed.csv / Scopus.csv  # 初回検索（第1波）
│   ├── scopus_wave2_20260730.ris   # Rev.6第2波 Scopus API 生出力（2,542件）
│   ├── acm_wave2_20260803.csv / ieee_wave2_20260810.csv  # 第2波 ACM 9,630 / IEEE 361
│   └── scopus_wave2_20260730.csv   # ★上記RISのZotero取込→CSVエクスポート（2,542件, Abstract 100%）
├── CORE.csv                     # CORE学会ランキング（1,955エントリ）
├── scimagojr 2025.csv           # SJRジャーナルランキング（50,326エントリ）
│
├── pipeline.py                  # ★ メインパイプライン (Phase 1-3)
├── prisma_screening.py          # キーワード除外スクリーニング（単体実行用）
├── venue_screening.py           # 学会ランクスクリーニング（プロトタイプ版）
├── simulate_screening.py        # ★ 足切りシミュレーション・DB集計ツール
│
├── scripts/                     # 検証・監査 / API連携スクリプト（要 requests）
│   ├── api_search_common.py     # 共通部品: クエリビルダー・polite_get・RIS出力・.env読み込み
│   ├── db_search_ieee.py        # IEEE Xplore API 検索（第2波。※要 IEEE_API_KEY）
│   ├── db_search_scopus.py      # Scopus API 検索（第2波）
│   ├── snowball_search.py       # ★ スノーボーリング（引用探索）→ §8
│   ├── enrich_screening_abstracts.py  # ★ 判定対象の要旨を DOI から補完（Rev.16）
│   ├── enrich_abstracts.py      # Crossref→S2 で Abstract 補完（DOIベース）
│   ├── export_completeness_audit.py  # ★エクスポートの打ち切り・欠落検出（§4.1）
│   ├── merge_raw.py             # ★raw/*.csv → 統合生データ生成（Source_DB 付与・PubMed除外）
│   ├── merge_bib.py             # 年スライスの .bib を引用キー単位で一意化して統合
│   ├── known_item_test.py       # Known-Item Test（recall測定 → known_item_analysis.md）
│   ├── make_screening_sheets.py # ★Phase 3b 判定シート生成（stage 1・CSV）→ §11
│   ├── make_screening_xlsx.py   # ★判定シートの Excel 版（評価者の作業ファイル）
│   ├── make_screening_stage2.py # ★stage 2（著者の Exclude 分を第2評価者へ）
│   ├── score_screening.py       # ★Phase 3b 集計（κ・協議リスト・最終判定）
│   └── *_audit.py               # Venue照合・正規化衝突・PubMed固有件数などの監査
├── screening/                   # ★Phase 3b の判定シート一式 → §11
│   ├── assignment.csv           # 割当の正（record_id・calibration・第2評価者）
│   ├── sheet_<id>.csv / .xlsx   # stage 1 の判定シート（評価者ごとに独立）
│   └── stage2_sheet_<id>.csv    # stage 2（著者の記入完了後に生成）
├── outputs/                     # 上記スクリプトの出力（監査CSV・実行ログ）
│   ├── enriched_abstracts.csv   # ★ DOI から補完した要旨のキャッシュ（人手判定の材料専用）
│   ├── snowballing_log.csv      # スノーボーリング結果（17列。判定は判定シートに統合）
│   └── snowballing_log_pre20260810.csv  # 旧12列版（Rev.10 改修前。経緯として保存）
│
├── step1_dedup.csv              # Phase 1 出力: 重複削除済み（18,342件、フィールドマージ済み）
├── step1_5_filter_included.csv  # Phase 1.5 出力: フィルタ層 通過（6,317件）
├── step1_5_filter_excluded.csv  # Phase 1.5 出力: フィルタ層 除外（12,025件）
├── step2_rank_included.csv      # Phase 2 出力: 高ランクVenue通過（1,179件）
├── step2_rank_excluded.csv      # Phase 2 出力: 低ランクVenue除外（9,634件）
├── step3_kw_included.csv        # Phase 3a 出力: ★最終候補（795件）
├── step3_kw_excluded.csv        # Phase 3 出力: キーワード除外（1,082件）
│
├── pipeline_log.txt             # パイプライン実行ログ（詳細・最新値はここ）
│
├── .env                         # APIキー（**git管理外**。IEEE / Scopus / Semantic Scholar）
├── .env.example                 # 変数名テンプレート（コミット可・値は空）
├── venue_aliases.csv            # 著者確認済みVenueエイリアス表（Phase 2 の最優先照合）
├── self_scale_references.csv    # ★正式 gold set（SearchScope列: in-scope 17件 / background 8件）
├── README.md                    # このファイル
└── docs/                        # 全文書（2026-08-20 に3分類へ再編）
    ├── protocol/                # ★ルールを定める文書。ここが一次情報
    │   ├── rule.md                    # 研究プロトコル本体（目的・RQ・PICOS・κ閾値方針・参考文献§5）
    │   ├── screening_protocol.md      # Phase 3b の運用手順
    │   ├── snowballing_protocol.md    # 引用探索の手続き
    │   ├── search_strings.md          # DB別検索式の記録（PRISMA Item #7）
    │   └── search_replication.md      # 検索記録の復元・再実行手順
    ├── log/                     # ★記録。時系列で追記し、過去分は遡及修正しない
    │   ├── protocol_changelog.md      # プロトコル変更履歴（Rev.1〜21）— 方針の一次情報
    │   ├── PROGRESS_LOG.md            # 進捗ログ（セッションログ・次回タスク）
    │   └── consistency_audit_log.md   # 文書間の不整合と、その決定ログ
    └── reference/               # 分析・検討・配布物・入出力
        ├── methodology_rationale.md      # Phase 3b までの手法と意図・想定質問
        ├── screening_method_alternatives.md # 代替手法10件の比較検討
        ├── methodology_decision_Rev7.md  # 検索方法論のデータ検証・確定
        ├── normalization_design.md       # Venue正規化の設計案（案1〜6、未適用）
        ├── reviewer_briefing.md          # 評価者向け説明資料（詳細版）
        ├── reviewer_briefing_preread.{md,tex,pdf}  # 事前配布資料
        ├── known_items.md                # 既知文献リスト（known_item_test.py が読む）
        └── known_item_analysis.md        # ★自動生成: 脱落分析
```

> **文書の3分類（2026-08-20）:**
> **`protocol/`** はルールを定める文書で、ここが一次情報。
> **`log/`** は時系列の記録で、**過去のエントリは遡及修正しない**（当時の記述として正しいため。
> 訂正が要る場合は注記を追加する）。
> **`reference/`** はそれ以外（分析・検討・配布物・スクリプトの入出力）。

### 4.1 データ取り込みの検証（2026-08-03 追加）

DB からのエクスポートは**上限で黙って打ち切られる**ことがある（ACM=1,000件・IEEE=2,000件を実測）。
打ち切りは新しい年に偏るため、そのまま Known-Item Test を回すと「recall が低い」という
**誤った結論**が出る。取り込み時は必ず次の順で検証する。

```bash
# 1. エクスポートの完全性を検査（ネットワーク不要）
python -X utf8 scripts/export_completeness_audit.py --expect acm_wave2=14340

# 2. 統合生データを組み立てる（Source_DB 列を付与、PubMed は Rev.8 により既定で除外）
python -X utf8 scripts/merge_raw.py --dry-run   # 件数の内訳を確認
python -X utf8 scripts/merge_raw.py             # → ResearchVR4.csv
```

`export_completeness_audit.py` が見るのは、件数の打ち切り疑い・ファイル内/間の重複・
期待ヒット数との一致・**gold set の捕捉状況**・年分布。とくに gold set 照合は
DOI一致とタイトル一致を**別々に**判定し、「タイトルは一致するが DOI が違う」ケースを
`SUSPECT`（同名別論文を捕捉している疑い）として報告する。これは Known-Item Test の
recall を過大評価させる要因なので、`SUSPECT` は `HIT` として数えない。

`merge_raw.py` は `raw/*.csv` を連結して `ResearchVR4.csv` を作る。重複削除はしない（Phase 1 の責務）。
`known_item_test.py` は `ResearchVR*.csv` の名前昇順で最後を step0 に使うため、
**ファイルを置くだけで検証対象が最新の統合データに切り替わる**。

> **注（gold set の所在）:** `known_item_test.py` は `known_items.csv` → `known_items.md` →
> `self_scale_references.csv` の順に探索する。`known_items.md` の表は有効行0のテンプレートなので、
> 実際に使われる gold set は **`self_scale_references.csv`** に一本化されている（Rev.7）。
> in-scope を 15〜25件へ拡充する際は `self_scale_references.csv` に `SearchScope=in-scope` 行を追加すること。

> **注（`rule.md` の反映状況）:** DB構成=3DB・scope=TA・Threats への追記は Rev.8 で確定済みだが、
> **`rule.md` 本文への反映は第2波再検索の完了後にまとめて行う**予定（`docs/log/PROGRESS_LOG.md` の
> 「次回やること」）。それまでの間、方針の最新状態は `docs/log/protocol_changelog.md` を見ること。

> **注（2026-07-21 のファイル整理）:** 手書きのプロトコル文書は `docs/` に集約した。
> `README.md`（入口）と、`known_item_test.py` が直接読み書きする `known_items.md` /
> `known_item_analysis.md` はスクリプト結合のためルートに据え置き。
> **データ・コードのパスは未変更**（`raw/` `outputs/` `scripts/` `step*.csv` `pipeline.py` はそのまま）。

---

## 5. パイプライン詳細

`pipeline.py` は3フェーズを一括実行するメインスクリプト。  
入力: 統合生データ / `CORE.csv` / `scimagojr 2025.csv` / `venue_aliases.csv`

> **注:** コード上の既定入力（`pipeline.py:23` の `DEFAULT_INPUT`）は **`ResearchVR2.csv` のまま**だが、
> 現行の公式実行は **`--input ResearchVR4.csv`** で行われている（`pipeline_log.txt` の Input 行が正）。
> 既定値の変更は公式再実行のタイミングで行う（step ファイル凍結中のため現在は触らない）。

### Phase 1: 重複削除 (`pipeline.py`)

| 重複検出基準 | 削除件数 |
|---|---|
| DOI完全一致 | 1,824件 |
| Zotero Key完全一致 | 0件 |
| タイトル完全一致（小文字正規化後） | 315件 |
| **合計削除** | **2,139件** |

**実装の要点:**
- DOI → Key → Title の優先順位で重複を検出
- 先に登場したレコードを正として保持（後続レコードを削除）

---

### Phase 1.5: フィルタ層 — 正規化クエリの再適用 (`pipeline.py`, Rev.13)

**取得後に、統合クエリの3概念群（G1∧G2∧G3）を Title+Abstract へ一律に再適用する段。**

**なぜ必要か:** DB ごとに検索の当たり方が違う。実測で判明しているものだけでも

| DB | 差異 |
|---|---|
| Scopus | 第1波は `TITLE-ABS-KEY`、第2波は `TITLE-ABS`（Rev.11） |
| IEEE | 第1波はより広いフィールド指定。第2波に現れない1,077件のうち TA で3群成立は **4.7%**（Rev.11） |
| ACM | 第2波は Title 検索と Abstract 検索の**和集合**。フィールド横断の一致を落とす（Rev.11） |

このまま統合すると「**どの DB で拾われたか**」で適格性が変わってしまう。取得後に
同じクエリを1回だけ適用してこの差を吸収する（`methodology_decision_Rev7.md` 方針3の実装）。

**配置:** 選定基準（Phase 2・3a）**より前**、重複削除**より後**。
「取得の差を均す処理」と「適格性で落とす処理」は性格が違うので段を分け、PRISMA でも
別の段として報告する。重複削除より後なのは、同じ論文の複数コピーで判定が割れるのを避けるため。

**フェイルセーフ（設計の要）:** 要旨が無いレコードは**判定不能であって不適格ではない**。
`hold` として保留し、除外せず人手スクリーニングへ送る。タイトルのみで判定すると
要旨なし567件のうち566件が落ち、gold set 4件を失う（＝中身ではなくメタデータ品質による
除外になってしまう）。この設計で **gold set の脱落は 0件**。

**出力列:** `Filter_Layer`（`pass` / `hold` / `fail`）、`Filter_Layer_Reason`（不成立の概念群）。
`step1_5_filter_included.csv` / `step1_5_filter_excluded.csv` に分けて保存する。

#### Phase 1.5 結果

| 判定 | 件数 | 扱い |
|---|---|---|
| pass（3群成立） | 2,610 | 次段へ |
| hold（要旨なし＝判定不能） | 3,707 | **除外しない**。次段へ送り人手判定に回す |
| fail（要旨があり3群不成立） | 12,025 | 除外 |
| **通過計** | **6,317** | |

> **却下した代替案:** キーワードスコアによる足切り（0〜3点の閾値）は採用していない。
> gold set 検証でスコア≤1の除外は **12件中3件（#4 Being Barbie / #12 Pouke / #18 Kitazaki）を落とす**
> （**Rev.13 実施時点の gold set 12件に対する検証**。Rev.14 で17件へ拡充した後は再検証していないが、
> 却下の理由は下記(a)(b)のとおり構造的で、件数に依存しない）。
> 理由は構造的で、(a) スコアは「関連性」ではなく「検索クエリと同じ語彙を使っているか」を
> 測っている（スケール知覚カテゴリのヒット率2.5%）、(b) 要旨欠落と交絡し、要旨なし文献の
> 95.1% がスコア1点以下になる。詳細は `docs/log/protocol_changelog.md` Rev.13。

### Phase 2: 学会ランクスクリーニング (`pipeline.py`)

#### Venue照合ロジック（実装の実行順）

**Step 0: 著者確認済みエイリアス表**（`venue_aliases.csv`、Rev.6 で追加）
— 他のいずれの照合よりも**先に**参照する。正規化による同名衝突の誤照合を是正するための最優先テーブル
（Presence誌29件・TAP誌49件の誤照合を修正、旧称 IEEE VR 8件をA*として救済）。

**Step A: CORE 照合**（`best_core_match`。この4段を上から順に試す）

1. **正規化タイトル完全一致** — ストップワード・年号・括弧内表記を除去した正規化後のキー
2. **小文字元タイトル一致** — `venue.lower()`
3. **括弧内頭字語抽出** — `"2010 IEEE VR Conference (VR)"` → `"VR"` を抽出して照合
4. **ファジーマッチング（CORE限定）** — `difflib.SequenceMatcher` による類似度 ≥ 0.82

**Step B: SJR 照合**（`best_sjr_match`。CORE で1件もヒットしなかった場合のみ）

1. **ISSN ルックアップ**（最速）
2. **正規化タイトル完全一致** — ファジーは50,326エントリでは遅すぎるため**使わない**

> ⚠️ **既知の順序問題（未修正）:** Step A の**ファジー照合が Step B の完全一致より先に走る**ため、
> ジャーナルが誤って CORE の類似会議名にマッチしうる。最大の実例は **PACM HCI 82件**
> （SJR に完全一致があるのに CORE fuzzy が先に拾ってしまう）。全数監査の結果、
> 正規化の同名衝突は 899キー・採否が反転するもの 426件（うちデータ出現 74キー）で、
> `venue_aliases.csv` に MANUAL 行として自動追記済み。恒久対策は
> `docs/reference/normalization_design.md` の6案（推奨: 案6 順序修正 + 案1 種別マーカー +
> 案3 短キーガード + 案4 サニティチェック）で、**適用は公式再実行時**。

#### 採用基準

| ソース | 採用基準 |
|---|---|
| CORE Ranking | **A** または **A*** のみ採用 |
| SJR (Scimago) | **Q1** のみ採用（ISSNによる高速ルックアップあり） |

#### 正規化処理の内容

```python
# 4桁年号 (e.g. 2024) を除去
# 序数 (e.g. 1st, 22nd) を除去
# 括弧内テキストを除去
# 非単語文字を除去
# ストップワード除去: proceedings, conference, journal, transactions,
#                   symposium, international, the, of, on, in, and,
#                   annual, workshop, adjunct, abstracts, poster ...
```

#### Phase 2 結果

**通過（`Ranking_Source` 列の実測）**

| 分類 | 件数 |
|---|---|
| SJR Q1 | 838件 |
| CORE A/A* | 193件 |
| CORE A/A*（エイリアス経由） | 125件 |
| SJR Q1（エイリアス経由） | 23件 |
| **通過合計** | **1,179件** |

**除外（`Excl_Reason_Phase2` 列の実測）**

| 分類 | 件数 | 割合 |
|---|---|---|
| **Venue未照合（CORE/SJR に存在しない）** | **3,085件** | **60.0%** |
| CORE 低ランク（B/C等） | 1,165件 | 22.7% |
| SJR 非Q1（Q2/Q3/Q4/-） | 888件 | 17.3% |
| **除外合計** | **5,138件** | 100% |

> 通過 1,179 + 除外 5,138 = 6,317（Phase 1.5 通過分）と一致する。
> **除外の60%は「ランクが低いから」ではなく「照合できなかったから」**であり、
> Threats to Validity の筆頭項目になる（`docs/reference/methodology_rationale.md` §3）。

> 入力は Phase 1.5 通過分の 6,317件。Rev.12 の正規化改修（種別マーカー・短キーガード・
> サニティチェック・照合順序の修正）が適用されており、`Match_Stage` 列でどの段で照合したかを追える。

> **Venue フィルタの取りこぼし（Threats に記載必須）:** Known-Item Test の in-scope 17件のうち
> **5件がこの Phase 2 で脱落**している。Rev.12 の改修で内訳が
> 「照合漏れ3 / ランク不足1 / 基準どおり1」→ **「照合漏れ1 / ランク不足3 / 基準どおり1」**に変わった。
> #8 SAP と #13 MIG は「リストに無い」のではなく「正しく照合したうえで CORE B・C だった」ことが
> 判明しており、**Threats の主張が「照合の不具合」から「品質基準そのものの帰結」に変わる**。
> 内訳は `outputs/venue_dropped_known_items.csv`、回収手段はスノーボーリング（§8）。

---

### Phase 3: キーワード除外スクリーニング (`pipeline.py`)

Title + Abstract Note を結合したテキストに対して正規表現マッチングを実施。  
**いずれかのカテゴリにヒットした文献を除外**（大文字小文字区別なし、単語境界ガード `\b` 適用）。

#### 除外カテゴリとキーワード

**Cat1: VR/没入外スコープ**（非没入型ディスプレイ・AR/MR等）

| キーワードパターン | ヒット件数 |
|---|---|
| `\baugmented reality\b` | 162件 |
| `\bar\b` | 138件 |
| `\bmixed reality\b` | 61件 |
| `\bmr\b` | 35件 |
| `\bsmartphone\b` | 22件 |
| `\btablet(?:\s+computer)?\b` | 13件 |
| その他（360動画・flat screen・CAVE等 8パターン） | 27件 |

**Cat2: 技術論文・非実証研究**（レンダリング・GPU・アルゴリズム等）

| キーワードパターン | ヒット件数 |
|---|---|
| `\bpoint\s+cloud\b` | 12件 |
| `\bgpu\b` | 11件 |
| `\breal[- ]?time\s+rendering\b` | 9件 |
| その他（rendering/segmentation/optimization algorithm 等 11パターン） | 42件 |

**Cat3: 臨床・医療研究**（患者・リハビリ・手術等）

| キーワードパターン | ヒット件数 |
|---|---|
| `\bpatient[s]?\b` | 539件 |
| `\brehabilitation\b` | 287件 |
| `\bsurgery\b` | 89件 |
| `\bclinical\s+(?:trial\|study\|outcome\|setting\|population)\b` | 78件 |
| `\bphysical\s+therapy\b` | 42件 |
| `\bschizophrenia\b` | 26件 |
| その他（stroke・exposure therapy・dementia 等 20パターン） | 213件 |

#### Phase 3 結果

| 分類 | 件数 | 割合 |
|---|---|---|
| **通過（最終候補）** | **795件** | **67.2%** |
| Cat1 除外（非没入・スコープ外） | 112件 | — |
| Cat2 除外（技術・非実証） | 24件 | — |
| Cat3 除外（臨床・医療） | 262件 | — |
| **除外合計** | **383件** | **32.8%** |

> **注1:** 上のキーワード別の値は**パターンごとのヒット件数**であり、1件の文献が複数パターンに
> 該当しうるため、合計は「Cat*n* 除外件数」を上回る（例: Cat3 はヒット計 1,274 に対し除外 765件）。
> 全パターンの内訳と「ヒット0のパターン」は `pipeline_log.txt` を参照。
>
> **注2:** 1件の文献が複数カテゴリに該当する場合があるため、カテゴリ別件数の合計と除外合計も一致しない。

---

## 6. スクリーニング実績（PRISMA数値）

```
元データ          : 26,434 件 (ResearchVR4.csv)
│                    内訳: ACM 7,997+9,630 / IEEE 1,276+297(更新)+361 / Scopus 4,331+2,542
│                    ※PubMed は Rev.8 で不使用に確定。この内訳に含まない
│
├─ Phase 1 重複削除 ─────────────────── -8,092件
│   └─ 重複削除後  : 18,342 件   （+ 重複コピーから Abstract 4,172 / ISSN 1,474 を補完）
│
├─ Phase 1.5 フィルタ層 ─────────────── -12,025件
│   └─ 通過        : 6,317 件    （pass 2,610 / hold 3,707 ＝要旨なしで判定不能）
│
├─ Phase 2 学会ランクスクリーニング ──── -5,138件
│   └─ 高ランク通過: 1,179 件
│
└─ Phase 3a キーワード除外 ──────────── -384件
    └─ 左カラム確定 : 795 件  ← step3_kw_included.csv
```

**引用探索（PRISMA 右カラム、§8）:**

```
475 行 発見
├─ 既存コーパスに既出 ─────────────── -158件（左カラムで同定済み。二重計上しない）
├─ シード間の重複 ────────────────── -30件
├─ タイトル取得不能 ──────────────── -3件（手作業で同定・要対応）
└─ Phase 3a キーワード除外 ────────── -28件
    └─ 右カラム確定 : 257 件
```

> 右カラムには **Phase 1.5 と Phase 2 を適用していない**（理由は §8）。
> Phase 3a と Phase 3b は左右で同一基準。

**Phase 3b（人手二重スクリーニング）の判定対象:**

| 取得経路 | 件数 |
|---|---|
| データベース検索（左カラム） | 795 |
| 引用探索（右カラム） | 257 |
| **合計** | **1,052** |

**liberal accelerated 方式**（Rev.17）: 1名の Include で通す / Exclude には2名。

| 段 | 内容 | 担当 |
|---|---|---|
| stage 1 | 全1,052件を著者が判定。うち**校正セット164件（15%）は3名全員** | 著者 1,052 / 他2名 各164 |
| stage 2 | 著者が Exclude / Unsure にしたものだけ第2評価者が確認 | 2名で分担 |

**κ は校正セット164件でのみ算出する。** 除外プールだけで計算すると著者の判定に分散が無く
**κ が常に 0** になるため（`docs/log/protocol_changelog.md` Rev.17）。
判定シートは `screening/`（§10）。
要旨欠落は **191件（18.2%）**＝左63 + 右128。Rev.16 で DOI から **134件**を外部補完した結果
（補完前は325件・30.9%）。`abstract_source` 列で `database` / `enriched` / `none` を識別できる。

> **補完した要旨で自動除外を掛け直していない。** 補完は人手判定を助けるためのもので、
> 既に「判定不能なので人手に委ねる」と決めたレコードの扱いを機械側に巻き戻さない。
> 理由は `docs/log/protocol_changelog.md` Rev.16（要約: PRISMA 2020 は自動ツールによる除外を
> スクリーニングの手前に置き人手除外と分けて報告することを求めており、補完後の再適用は
> 検索が一度も見ていないテキストで自動除外を発動させることになる）。

**DB間重複の内訳（初回分、重複除去の報告用）:**
PubMed∩Scopus 606 / Scopus∩IEEE 352 / Scopus∩ACM 142 / PubMed∩IEEE 39 / ACM∩IEEE 0 / ACM∩PubMed 0
（`outputs/raw_db_audit.csv`）

### 検索の網羅性検証（Known-Item Test）

`scripts/known_item_test.py` が gold set（`self_scale_references.csv`、`SearchScope` 列で in-scope 17件）を
各 step ファイルに突き合わせ、recall を測定して `known_item_analysis.md` を生成する。

| 段階 | 生存 | recall |
|---|---|---|
| step0 統合生データ（検索式で拾えたか） | 13/17 | **76.5%** |
| step1 重複削除後 | 13/17 | 76.5% |
| step1.5 フィルタ層通過後 | 11/17 | 64.7% |
| step2 Venueランク通過後 | 5/17 | **29.4%** |
| step3 最終候補 | 5/17 | 29.4% |

- **step0 で4件脱落（検索式・カバレッジの問題）:** Frontiers in Virtual Reality 3件 =
  DBカバレッジ欠落（同誌はSJR Q1）、Being Barbie 1件 = クエリG1ギャップ
  （PLoS ONE は索引済みなのでライブラリ追加では直らない）→ Rev.6 の G1 拡張で対処。
- **step2 で6件脱落（Venueフィルタの問題）** — recall 低下の最大要因はここ。§5 Phase 2 の注記を参照。
- Phase 1・Phase 3 での脱落は0件。
- **目標は step0 ≥ 80%。** 上記は第1波データでの測定値であり、第2波再検索後に再測定する。
  なお3DB化（PubMed除外）は recall に影響しない見込み（PubMed 固有の known-item 寄与が0のため）。

---

## 7. 追加分析ツール

`simulate_screening.py` は **step3_kw_included.csv** に対して、  
**読み取り専用・ファイル出力なし**でコンソールに集計結果を表示するツール。

> **本節の数値は 2026-08-20 に現行データ（`step3_kw_included.csv` = 795件）で再実行した結果。**
> 旧版は 2026-05-25・1,784件時点の集計だった（`docs/log/consistency_audit_log.md` 論点6）。

実行方法:
```bash
python -X utf8 simulate_screening.py
```

---

### タスク 1A: 引用数による足切りシミュレーション

> ⚠️ **注意:** このCSVはZotero形式のエクスポートであり、**引用数列が存在しない**（`Citation Count` / `Cited by` 等の列なし）。  
> 現状では全件を「引用数=0（不明）」として処理した**最悪ケースシミュレーション**となる。  
> 実運用では **Semantic Scholar API** 等から引用数を別途取得してCSVに追加することを推奨。

**フェイルセーフロジック:**  
発行年が **2023年以降** の論文は、引用数に関わらず足切りから除外（直近論文は引用蓄積期間が短いため）

| 閾値 | 除外件数 | 残存件数 | 残存率 | フェイルセーフ救済 |
|---|---|---|---|---|
| 引用数 < 5 | 441件 | 354件 | 44.5% | 354件 |
| 引用数 < 10 | 441件 | 354件 | 44.5% | 354件 |
| 引用数 < 20 | 441件 | 354件 | 44.5% | 354件 |

> 引用数が全件不明（0扱い）のため、閾値によらず結果が一定（フェイルセーフ対象の354件 = 2023年以降のみ残存）。

**年代別内訳（引用数補完後の判定参考）:**

| 年代 | 件数 |
|---|---|
| 2023年以降（フェイルセーフ対象） | 354件 |
| 2022年以前（足切り対象になりうる） | 441件 |
| 発行年不明 | 0件 |

**発行年分布の概要（step3_kw_included.csv）:**

| 期間 | 件数 |
|---|---|
| 〜2014年 | 112件 |
| 2015〜2019年 | 151件 |
| 2020〜2022年 | 178件 |
| 2023〜2024年 | 163件 |
| 2025〜2026年 | 191件 |

---

### タスク 1B: キーワードスコアによる足切りシミュレーション

各文献の Title + Abstract Note を結合し、3カテゴリのキーワードヒット数（0〜3点）を算出。

#### スコア定義

| カテゴリ | キーワード群 |
|---|---|
| Cat1 VR環境 (1点) | `"Virtual Reality"` / `VR` / `HMD` / `"Virtual Environment"` |
| Cat2 身体化 (1点) | `"Body ownership"` / `Embodiment` / `Avatar` / `"Virtual body"` |
| Cat3 スケール知覚 (1点) | `"Size perception"` / `"Body size"` / `"Eye height"` / `"Perceived size"` / `"Spatial scale"` / `"Scale perception"` |

各カテゴリ内で1つでもヒットすれば1点（大文字小文字区別なし）。

#### カテゴリ別ヒット件数

| カテゴリ | ヒット件数 | ヒット率 | 備考 |
|---|---|---|---|
| Cat1 VR環境 | 701件 | 88.2% | 検索クエリ由来のため高ヒット率 |
| Cat2 身体化 | 249件 | 31.3% | |
| Cat3 スケール知覚 | 50件 | 6.3% | **極めて低率 ← 要注意** |

> Cat3のヒット率が6.3%と著しく低い理由として、スケール知覚の記述が Abstract でなく Full-text に留まるケースが多い可能性がある。Abstract 欠損が170件（21.4%）存在する点も影響している。
>
> **この低ヒット率が、キーワードスコアによる足切りを却下した根拠のひとつ**（§Phase 1.5 の「却下した代替案」）。

#### スコア別 件数内訳

| スコア | 件数 | 割合 | 解釈 |
|---|---|---|---|
| **0点** | **78件** | **9.8%** | 全カテゴリ不一致 → 最優先除外候補 |
| **1点** | **460件** | **57.9%** | 1カテゴリのみ一致 → 除外候補 |
| **2点** | **231件** | **29.1%** | 2カテゴリ一致 → 要精査 |
| **3点** | **26件** | **3.3%** | 全カテゴリ一致 → コアトピック確定 |

#### スコア閾値別 足切りシミュレーション

| 足切り条件 | 除外件数 | 残存件数 | 残存率 |
|---|---|---|---|
| スコア < 1点を除外 | 78件 | 717件 | 90.2% |
| スコア < 2点を除外 | 538件 | 257件 | 32.3% |

#### タスク1A × 1B クロス集計マトリクス（引用数 < 5、フェイルセーフ適用）

|  | KW=0 | KW=1 | KW=2 | KW=3 | 合計 |
|---|---|---|---|---|---|
| 除外（引用数不足）| 40 | 262 | 125 | 14 | **441** |
| 残存（引用数OK）| 38 | 198 | 106 | 12 | **354** |

> 引用数OK（2023年以降）の中でもKW=1が198件と最多。これらは「VR環境」のみヒットしており、身体化・スケール知覚のキーワードを含まない → Phase 4 全文審査で慎重に評価すべき層。

---

### タスク 2: 取得元データベース集計

URL列のドメイン、DOIプレフィックス、Publisher列を優先順位付きで総合判定。

**判定優先順位:** URL内ドメイン → DOIプレフィックス → Publisher名

| データベース | 件数 | 割合 | 判定基準 |
|---|---|---|---|
| **ACM** | **186件** | **23.4%** | `dl.acm.org` / DOI `10.1145` |
| **IEEE** | **181件** | **22.8%** | `ieeexplore.ieee.org` / DOI `10.1109` |
| **Scopus/Elsevier** | **426件** | **53.6%** | `scopus.com` / `sciencedirect.com` / DOI `10.1016` |
| PubMed/PsycInfo | 0件 | 0.0% | `pubmed.ncbi.nlm.nih.gov` / DOI `10.1037` |
| Others/不明 | 2件 | 0.3% | 上記以外 |
| **合計** | **795件** | **100.0%** | |

> PubMed/PsycInfo が0件なのは、これらのデータベース由来の文献が Scopus/Elsevier 経由でインポートされ、
> URL が scopus.com になっているためと考えられる（**取得元DBの内訳は本集計ではなく
> `scripts/raw_db_audit.py` による `raw/` のDB別コレクション実測を正とする** — §6の内訳を参照）。

**Others/不明（2件）の内訳（DOIプレフィックス）:**

| DOIプレフィックス | 件数 | 出版社 |
|---|---|---|
| `10.1162` | 2件 | MIT Press（Presence 誌等） |

---

## 8. スノーボーリング（引用探索）

`scripts/snowball_search.py` — Semantic Scholar Graph API + Crossref による前方・後方引用探索の自動化。
手続きの定義は `docs/protocol/snowballing_protocol.md`、本節はその**実装**の説明。

> ⚠️ **外部APIに通信する**（Semantic Scholar / Crossref）。既定では著者が実行する。
> スクリプトが行うのは「取得」と「機械的に分かる情報の付与」までで、**PICOS採否は人が判断する**。

> **実行状況（Rev.15、2026-08-16）:** シード7件（主題6件 + 定義シード #3 は後方探索のみ）で実行。
>
> ```
> 475行 → 既存コーパスに既出 -158 → シード間重複 -30 → タイトル取得不能 -3
>       → Phase 3a キーワード除外 -28 → 257件（判定対象）
> ```
>
> **右カラムに適用する段・しない段**（`docs/protocol/snowballing_protocol.md` §4.3b）:
>
> | 段 | 適用 | 理由 |
> |---|---|---|
> | Phase 1.5 フィルタ層 | **しない** | DB検索で取得していない文献に「DB間のscope差」は存在しない |
> | Phase 2 Venueランク | **しない** | 適用すると165件(64%)が消えるが、その83%は品質判断ではなく**照合失敗**（未照合88 / venue名なし49）。`Science`・`Cognition` や、回収対象そのものである `Presence`・`ICAT-EGVE` が落ちる |
> | Phase 3a キーワード除外 | **する** | PICOS 由来の適格性基準 |
> | Phase 3b 人手判定 | **する** | PRISMA 公式フロー図は右カラムで Title/Abstract 段を省略し全文評価へ直行する想定だが、本レビューの右カラムは機械生成で人手フィルタを経ていないため、**規定より慎重に**この段を設ける |
>
> ⚠️ **この非対称な運用に明確な前例は確認できていない。** 詳細と報告義務は
> `docs/log/protocol_changelog.md` Rev.15 を参照。

### 8.1 なぜ必要か

Known-Item Test で、in-scope 17件中 **6件が Phase 2 の Venue ホワイトリストで脱落**していることが判明した
（`outputs/venue_dropped_known_items.csv`: unmatched 3 / below_rank 2 / criterion 1）。
これは検索式では捕捉できているのに Venue 基準で落ちる取りこぼしであり、
検索式の改良（Rev.6 第2波）では解決しない。引用ネットワーク経由の回収がこの残余リスクを緩和する。
Scopus scope を TA に統一したこと（旧検索の実質 TITLE-ABS-KEY より -46%）の残余リスクも同じ枠で緩和する。

### 8.2 処理フロー

```
シード（既定6件）
  │
  ├─ ① paperId 解決 ───────── DOI があれば paper/DOI:{doi}、無ければタイトル検索でフォールバック
  │
  ├─ ② 双方向探索
  │     backward: S2 /references → 非開示なら Crossref の reference にフォールバック
  │     forward : S2 /citations  → offset ページングで取り切る（既定は無制限）
  │
  ├─ ③ 既存コーパスとの重複判定 → in_db_already 列 (Y/N)
  │
  └─ ④ CORE/SJR 照合（参考情報・フィルタしない） → venue_rank_note 列
              ↓
     outputs/snowballing_log.csv（追記モード）
     picos_decision / reason 列は空欄 ← 著者が記入
```

#### 実装上の重要な2点（2026-08-06 の初回実行で判明・修正済み）

**(a) 後方探索は S2 だけでは成立しない。**
Semantic Scholar は**出版社が参考文献を非開示にしている**論文があり（`elided by the publisher`）、
`data: None` が返って後方探索が丸ごと空になる。初回実行ではシード6件中**4件**（ACM 3・MIT Press 1）が該当した。
現在は **Crossref の reference リストにフォールバック**する（`ref_source` 列に経路を記録）。

| シード | S2 | Crossref |
|---|---|---|
| #3 Sense of Embodiment | 非開示 | 65件 |
| #7 Distortion in Perceived Size | 非開示 | 16件 |
| #8 Eye height and avatars | 非開示 | 24件 |
| #14 Gulliver's travels | データなし | 53件 |
| #13 Scaling Player Size | 15件 | — |
| #10 Dwarf or Giant | 非開示 | **未登録（取得不可）** |

Eurographics の DOI（`10.2312/...`）は Crossref に無いため、**#10 の後方探索だけは取得できない**。
Limitations に記載し、必要なら手作業で補完する。

**(b) 前方探索はページングしないと黙って切り捨てられる。**
S2 は1リクエスト最大1,000件・`offset+limit ≤ 10,000` の制約がある。
旧実装は `limit=200` 固定でページングしておらず、被引用の多い論文が切り捨てられていた
（実例: シード #3 は被引用 **1,497件**なのに 200件しか取れていなかった）。
現在は offset ページングで取り切り、`--limit-per-seed` の既定は **0（無制限）**。

### 8.3 シード選定

既定シードは **Venueフィルタで脱落した known-item 6件**。
`outputs/venue_dropped_known_items.csv` の `#` 列を `self_scale_references.csv` の `ID` 列で結合し、
`DOI_or_URL` 列から正規表現 `10\.\d{4,9}/\S+` で DOI 本体を抽出する（URL形式の混在に対応）。

`--seeds-csv` で任意のCSVに差し替え可能（`Title`/`DOI` 列。列名は `#`/`ID`/`seed_id`、
`DOI`/`DOI_or_URL` 等のエイリアス解決あり）。2ホップ目に著者が選んだ候補を再投入する用途を想定。
ホップ数は `docs/protocol/snowballing_protocol.md` §2.3 のとおり **2ホップまで**。**現在は1ホップのみ実施済み。**

### 8.4 重複判定の基準

`load_existing_keys()` が既存コーパスからキー集合を構築する。対象は:

| 入力 | 備考 |
|---|---|
| `raw/*.csv` | ZoteroのDB別エクスポート（第2波の取込済みCSVも自動的に含まれる） |
| `raw/*.ris` | API検索の生出力。Zotero未取込のデータも簡易パース（`DO  - `/`TI  - `/`ER`）で判定に含める |
| `step3_kw_included.csv` | 現行の最終候補 |

キーは **DOI優先・無ければ正規化タイトルに `T:` プレフィックス**を付ける方式で、
`scripts/known_item_test.py` と**同一基準**（正規化は小文字化 → 非英数字を空白へ → 空白圧縮）。
DOI は `https://doi.org/` `dx.doi.org/` `doi:` の接頭辞を剥がしてから比較する。

> **限界:** 発見側に DOI が無いレコード（初回実行で **135件**）はタイトル一致でしか判定できず、
> 表記ゆれがあると既出を見逃す。手作業での照合が必要（`docs/protocol/snowballing_protocol.md` §4.4）。

### 8.5 Venueランクの付与 — 採否には使わない

`pipeline.py` の `normalize_venue` / `load_core` / `load_sjr` を**そのまま import** して、
CORE → SJR → `未照合` の順で `venue_rank_note` 列に記録する。

**これは読む順序のトリアージ用の参考情報であり、採否の基準にはしない。**
スノーボーリングの目的が「Venue フィルタが落とした文献の回収」である以上、
回収したものに同じフィルタを掛け直せば同じ理由で再び落ちる。
実際、シード #10（ICAT-EGVE）・#13（MIG）は低ランク会場で脱落した文献であり、
Venue フィルタを適用すると**シード自身すら通らない**。

初回実行の新規1,403件のうち Phase 2 基準を満たすのは 579件、**満たさないのが 824件**。
**この824件こそが回収対象**である。

### 8.6 出力

`outputs/snowballing_log.csv`（**追記モード**。既存行は保持し、ヘッダは初回のみ書く）

| 列 | 内容 |
|---|---|
| `seed_id` / `seed_title` | シード論文 |
| `direction` | `backward` / `forward` |
| `found_title` / `found_doi` / `found_year` / `found_venue` | 発見された文献 |
| `in_db_already` | `Y`=既存コーパスに既出 / `N`=新規候補 |
| `venue_rank_note` | `CORE A*` / `SJR Q1` / `未照合` 等（**参考。採否に使わない**） |
| `ref_source` | `S2` / `Crossref` / `取得不可`（後方探索の取得経路。PRISMA-S 用） |
| `picos_decision` | **空欄** ← 著者が include/exclude を記入 |
| `reason` | **空欄** ← 著者が理由を記入 |

### 8.7 PRISMA 上の扱い

スノーボーリングで得た文献は PRISMA 2020 の**右カラム**（Identification of studies via other methods）を通り、
**Phase 4 の適格性評価で左カラムと合流**する。フロー図と各段階の定義は
`docs/protocol/snowballing_protocol.md` §4（Mermaid 図あり）を正とする。

初回実行（2026-08-06、1ホップ）の実測値:

| 段階 | 件数 |
|---|---|
| Seed set | 6 |
| Records identified via citation searching（一意化後） | 1,801 |
| うち既存コーパスと重複 → **右カラムに計上しない** | 398 |
| **New records via citation searching** | **1,403** |
| うち DOI 欠落（手作業で同定が必要） | 135 |
| Screened / Assessed | 未実施 |

**右カラムには Phase 2（Venue フィルタ）を適用しない**（§8.5 の理由）。
Title/Abstract 判定は Phase 3b と**同一基準**で行う。

### 8.8 通信の作法

`scripts/api_search_common.py` の共通部品を使う。

- `polite_get()` — 429/5xx を指数バックオフ（初回1秒、倍々）で最大5回再試行。401/403 等の 4xx は再試行せず即返す
- `load_dotenv()` — `.env`（git管理外）から `SEMANTIC_SCHOLAR_API_KEY` を読む。
  既に export 済みの環境変数は上書きしない。後方互換で `S2_API_KEY` も受理する
- APIキー無しでも動作するが、共有プールの rate limit が厳しくなる（キーはメール登録のみで発行可）
- Crossref は `ENRICH_MAILTO` を設定すると polite pool を使える（未設定でも動作する）

---

## 9. 分類体系 (Taxonomy)

Phase 4（全文審査）以降に使用する文献分類軸。

### (1) 介入モダリティ

| 分類 | 定義 |
|---|---|
| **Unimodal** | 視覚情報のみを操作（Visual-Global / Local / Perspective） |
| **Multimodal (two-way)** | 視覚を含む2感覚の同期（Visual-Tactile / Motor / Auditory） |
| **Multimodal (three-way+)** | 視覚を含む3感覚以上の同期・操作 |

### (2) 評価指標の志向性

| 分類 | 定義 |
|---|---|
| **Self-scale Dominant (S)** | 自己の身体サイズの変容を測定 |
| **World-scale Dominant (W)** | 外界の環境・物体・距離の変容を測定 |
| **Ambiguous/Mixed (A)** | 自己と世界の尺度が未分離・混在 |

### (3) 知覚の支配構造（ベイズ的分類）

| 分類 | 定義 | 意義 |
|---|---|---|
| **Stimulus-Overriding** | 物理的刺激（足音・振動・強い視覚同期等）が事前知識を上書きし、身体図式の更新に成功 | 「何の刺激が文脈の呪縛を解けるか」を明らかにする |
| **Context-Dominant** | トップダウンの事前知識（「ビルが縮むはずがない」等）が勝り、ミニチュア効果等の環境変容エラーが発生 | 「視覚単独・不十分な刺激の限界」を証明する |
| **Conflict / Threshold** | 刺激と文脈を意図的に衝突させ、知覚の反転境界線を調査 | 「〇倍まではStimulusが勝つが、それ以上はContextが勝つ」の議論に直結 |

> **理論的背景:** 多感覚（Multimodal）がStimulus-Overridingに寄与しやすい理由は、情報の信頼性に基づく**最尤推定（MLE）モデル**によって説明される。

---

## 10. 実行方法

### 前提条件

```bash
pip install pandas
pip install requests   # scripts/ の API 系スクリプト（検索・Abstract補完・スノーボーリング）に必要
```

**Windows では `-X utf8` フラグが必須**（付けないと出力・CSV読み書きで文字化けする）。

API 系スクリプトはリポジトリ直下の `.env` からキーを読む（`.env.example` をコピーして値を入れる。
`.env` は `.gitignore` 済みで**絶対にコミットしない**）。

```
IEEE_API_KEY=...               # developer.ieee.org（※2026-07-30 時点 ERR_403_DEVELOPER_INACTIVE で未解決）
SCOPUS_API_KEY=...             # dev.elsevier.com
SEMANTIC_SCHOLAR_API_KEY=...   # enrich_abstracts.py / snowball_search.py
```

### パイプライン全体実行（Phase 1〜3）

```bash
python -X utf8 pipeline.py
# オプション指定の場合:
python -X utf8 pipeline.py --input ResearchVR3.csv --core CORE.csv --sjr "scimagojr 2025.csv" --outdir ./
```

> ⚠️ 実行すると `step*.csv` と `pipeline_log.txt` が**上書きされる**。現行の step ファイルは
> Rev.6 以前の状態で凍結中（§6）なので、公式再実行のタイミングは
> `docs/log/PROGRESS_LOG.md` の方針に従うこと。

### 追加分析（足切りシミュレーション・DB集計）

```bash
python -X utf8 simulate_screening.py
```

### キーワード除外スクリーニング単体実行

```bash
python -X utf8 prisma_screening.py --input step2_rank_included.csv --outdir ./
# ドライランモード（ファイル出力なし）:
python -X utf8 prisma_screening.py --dry-run
```

### 検索の網羅性検証（Known-Item Test）

```bash
python -X utf8 scripts/known_item_test.py
# → outputs/known_item_test.csv と known_item_analysis.md を再生成（ネットワーク不要）
```

### 第2波再検索（API検索）

> 外部APIに通信する。著者が実行すること。出力は RIS で、Zotero に専用コレクションで
> 取り込んでから CSV エクスポートし `raw/` に置く運用（`docs/protocol/search_replication.md` Option A/B）。
> **ACM には一般利用可能な検索APIが無いため手動エクスポートを継続する。**

```bash
# まず件数だけ確認（RIS を書かない）
python -X utf8 scripts/db_search_scopus.py --use-default-query --count-only
# 本実行 → raw/scopus_wave2_YYYYMMDD.ris
python -X utf8 scripts/db_search_scopus.py --use-default-query

# IEEE も同様（※現在 developer.ieee.org のアカウント有効化が未解決で 403）
python -X utf8 scripts/db_search_ieee.py --use-default-query --count-only
```

Scopus は既定 `--scope TITLE-ABS`（TA基準）。`--scope TITLE-ABS-KEY` も指定できるが、
scope 方針の変更にあたるので**プロトコル改訂なしに使わない**こと。

実行記録は `outputs/api_search_log.csv` に追記されるので、
これを下書きとして `docs/protocol/search_strings.md` の DB別記録表に verbatim で転記する。

### Abstract の補完（ACM 対策）

```bash
python -X utf8 scripts/enrich_abstracts.py \
  --in step1_dedup.csv --out outputs/enriched.csv --only-empty --limit 20
# --limit 0（既定）で無制限。Crossref の polite pool を使うため ENRICH_MAILTO の設定を推奨
```

ACM DL 由来のレコードは Abstract 充足率が極端に低い（欠落 7,655件）。
DOI をキーに Crossref → Semantic Scholar の順で補完する。
2026-07-30 の20件試験では **11/20（55%）成功・全て S2 経由**で、Crossref 経由は0件だった
（該当ACM論文に Crossref 側の Abstract メタデータが元々存在しないため。仕様であって不具合ではない）。

### スノーボーリング（引用探索）

> 外部APIに通信する（Semantic Scholar / Crossref）。§8 参照。

```bash
# 既定シード（Venue脱落6件）で前方・後方の両方向。取得上限は既定で無制限
python -X utf8 scripts/snowball_search.py

# Crossref の polite pool を使う場合（後方探索のフォールバックで使用）
ENRICH_MAILTO="you@example.com" python -X utf8 scripts/snowball_search.py

# 片方向のみ / 取得上限を明示
python -X utf8 scripts/snowball_search.py --directions backward --limit-per-seed 100

# 2ホップ目（著者が選んだ候補を再投入）
python -X utf8 scripts/snowball_search.py --seeds-csv outputs/snowballing_hop2_seeds.csv
```

> ⚠️ 出力は**追記モード**。同じ条件で再実行すると行が二重に増えるので、
> やり直す場合は `outputs/snowballing_log.csv` を削除してから実行すること。

---

## 11. Phase 3b: 人手スクリーニングの実施

手続きの定義は `docs/protocol/screening_protocol.md`、方針の決定経緯は
`docs/log/protocol_changelog.md` Rev.9 / Rev.17。本節は**実行手順**のみ。

### 11.1 判定対象と体制

判定対象 **1,052件**（DB検索795 + 引用探索257）。**liberal accelerated 方式**で、
**1名の Include で通す / Exclude には2名**を要する。

| 段 | 内容 | 担当 |
|---|---|---|
| stage 1 | 全1,052件を著者が判定。うち**校正セット164件（15%）は3名全員** | 著者 1,052 / 他2名 各164 |
| stage 2 | 著者が Exclude / Unsure にしたものだけ第2評価者が確認 | 2名で分担 |

Phase 3b のエラーは非対称（誤 Exclude は回復不能／誤 Include は Phase 4 の手間が増えるだけ）で、
単独スクリーニングは関連文献の **13%** を見落とす（2名体制は 3%）という RCT の実測がある。
**除外の方向にだけ2名を要求**することで、工数を抑えつつ感度を保つ。

### 11.2 手順

```bash
# stage 1: 判定シートを生成（CSV → Excel）
python -X utf8 scripts/make_screening_sheets.py
python -X utf8 scripts/make_screening_xlsx.py

#   → screening/sheet_<id>.xlsx を各評価者に配布
#   → 記入後に screening/ へ戻してもらう

# stage 2: 著者の記入完了後、Exclude/Unsure だけを第2評価者へ
python -X utf8 scripts/make_screening_stage2.py
python -X utf8 scripts/make_screening_xlsx.py --prefix stage2_

# 集計: κ・協議リスト・最終判定
python -X utf8 scripts/score_screening.py
```

### 11.3 設計上の要点

- **評価者ごとに独立したファイル**にしている。1枚のシートに両者の判定列を並べると、
  先に書いた側が後の側から見えて独立性が壊れ、κ が意味を失う。
  **stage 2 のシートにも著者の判定は入れていない**
- **割当は決定論的**（校正セットの抽出・第2評価者の振り分けとも文献キーの MD5）。
  乱数を使わないので再生成しても記入済みの作業は動かない
- **κ は校正セット164件でのみ算出する。** 除外プールだけで計算すると著者の判定が
  定義上すべて Exclude で分散が無く、**実際の一致率によらず κ が常に 0** になる
- `kw_groups`（概念群スコア）は**読む順序のトリアージ専用**。この値による自動除外はしない
- 判定シートは記入中は git 追跡しない（互いの判定が見えるため）。
  **完了後に `git add -f` で監査証跡として追跡に加える**

### 11.4 報告に必要な数値

- ペア別 Cohen's κ（3本）とその平均、Landis & Koch の解釈
  — **校正セット164件で算出したものであることを明記する**
- liberal accelerated で1名の Include により通過した件数（第2評価者を経ていない分）
- 一致件数 / 要協議件数、協議で解決した件数 / 解決せず Include に倒した件数
- Phase 3b の Include 件数（= Phase 4 の対象）と Exclude 件数
- 取得経路別（database / snowballing）の内訳 — PRISMA の左右カラム別報告用

---

## 12. 期待される知見と貢献

本分類データを用いた分析によって明らかにしたい知見:

| 分析軸 | 期待される発見 |
|---|---|
| **年代別Taxonomy変遷** | 多感覚刺激研究の開始時期 / HMD普及との相関 / 心理学との接合点 |
| **Venue別トレンド** | どの学会・論文誌でスケール知覚研究が扱われるか / 多感覚研究への移行が早かった場 |
| **タスク × モダリティ** | 静的距離推定には視覚が強く、動的インタラクション（歩行等）には行動随伴的な聴覚・触覚が必須という傾向の検証 |
| **非視覚パラメータの体系化** | 聴覚（ピッチ・残響・遅延）/ 触覚（周波数・振幅）の自己スケール操作への貢献 |
| **Social VR応用** | 他者アバタ存在環境 vs 単独環境でのスケール感覚研究の分布・未開拓領域の特定 |
| **個人差分析** | 被験者の身長・VR経験・性別が結果に与える影響（高身長 vs 低身長の巨大化アバタ順応速度の差異等） |

---

## 付記: 引用数の補完（未着手）

`step3_kw_included.csv` には引用数列が存在しない（Zotero標準エクスポートの制約）ため、
足切りシミュレーション（§7 タスク1A）は「全件0扱い」の最悪ケースにとどまっている。
実態に即した値を得るには DOI を用いて外部APIから引用数を取得する必要がある。

`scripts/enrich_abstracts.py`（Abstract補完）と同じ Semantic Scholar API で
`citationCount` フィールドを取れるため、同スクリプトの `polite_get` / `.env` 読み込みを
再利用するのが早い。**専用スクリプトは未整備・未着手。**

```python
# 取得したいフィールドの例（実装時の参考）
params = {"fields": "citationCount"}   # GET /graph/v1/paper/DOI:{doi}
```

なお引用数による足切り自体はプロトコル未確定の検討案であり、
採用する場合は `docs/log/protocol_changelog.md` に改訂として記録すること
（Known-Item Test で recall への影響を測るのが前提）。

---

*最終更新: 2026-07-30（README全体の実装・方針との突き合わせ）｜プロトコル: PRISMA 2020 準拠（〜Rev.8）*