# SurveyProtocol — VR自己スケール知覚 システマティック・レビュー

> **PRISMA 2020準拠**のスクリーニングパイプラインと集計ツールの実装ドキュメント。  
> VR空間における自己スケール感覚（Self-scale perception）の形成要因を網羅的に体系化するためのシステマティック・レビュープロジェクト。
>
> **現行の確定値 (2026-08-12 実行, Rev.13):** 入力 `ResearchVR4.csv`（26,434件 = 3DB × 第1波+第2波）
>
> ```
> 26,434 → 18,342（P1 重複削除）→ 6,317（P1.5 フィルタ層）→ 1,167（P2 Venue）→ 784（P3a キーワード）
> ```
>
> **⚠️ 本ドキュメントを読むときの前提（2026-08-12 時点）:**
> 1. **プロトコルは Rev.13 まで確定。`step*.csv` は Rev.13 で再実行済み**（2026-07-17 以来の凍結は解除）。
> 2. **§7 の追加分析の表は旧データ（2026-05-25, 最終候補1,784件）時点**の集計で、**未更新**。
>    再実行が必要（§7 冒頭の注記参照）。
> 3. プロトコルの決定経緯・最新方針は `docs/protocol_changelog.md`（〜Rev.13）と
>    `docs/search_strings.md` が一次情報。本 README と食い違う場合は **docs/ 側が正**。

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
11. [期待される知見と貢献](#11-期待される知見と貢献)

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
| **RQ3** | 視覚的なスケーリング操作単独では、どのような知覚的限界・錯誤が生じるか？（ミニチュア効果等の境界条件の整理） |
| **RQ4** | 多感覚統合モデルは自己スケール感覚の確定においてどのように機能し得るか？（MLEモデルに基づく理論的考察） |

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

> 正当化ドラフト（Threats to Validity へ転用可）は `docs/methodology_decision_Rev7.md` §Rev.8追記。

### 統合検索クエリ

**実際に実行されたクエリ（第1波、2026-07-17 著者確認により確定）:**

```
("Virtual Reality" OR "VR" OR "HMD")
AND ("Avatar" OR "Body" OR "Embodiment")
AND ("Size" OR "Scale" OR "Height" OR "Distance")
```

> ⚠️ rule.md 旧版・本README旧版に載っていた詳細クエリ（`"Virtual Environment"` `"Body ownership"`
> `"Size perception"` 等の複合語を含むもの）は**計画段階のものであり実行されていない**
> （`docs/protocol_changelog.md` Rev.5 で訂正）。

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
DB間の表記不一致を防いでいる（§4・`docs/search_strings.md`）。

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
│   ├── enrich_abstracts.py      # Crossref→S2 で Abstract 補完（DOIベース）
│   ├── export_completeness_audit.py  # ★エクスポートの打ち切り・欠落検出（§4.1）
│   ├── merge_raw.py             # ★raw/*.csv → 統合生データ生成（Source_DB 付与・PubMed除外）
│   ├── merge_bib.py             # 年スライスの .bib を引用キー単位で一意化して統合
│   ├── known_item_test.py       # Known-Item Test（recall測定 → known_item_analysis.md）
│   └── *_audit.py               # Venue照合・正規化衝突・PubMed固有件数などの監査
├── outputs/                     # 上記スクリプトの出力（監査CSV・実行ログ）
│   └── snowballing_log.csv      # スノーボーリング結果（採否列は著者記入）
│
├── step1_dedup.csv              # Phase 1 出力: 重複削除済み（18,342件、フィールドマージ済み）
├── step1_5_filter_included.csv  # Phase 1.5 出力: フィルタ層 通過（6,317件）
├── step1_5_filter_excluded.csv  # Phase 1.5 出力: フィルタ層 除外（12,025件）
├── step2_rank_included.csv      # Phase 2 出力: 高ランクVenue通過（1,167件）
├── step2_rank_excluded.csv      # Phase 2 出力: 低ランクVenue除外（9,634件）
├── step3_kw_included.csv        # Phase 3a 出力: ★最終候補（784件）
├── step3_kw_excluded.csv        # Phase 3 出力: キーワード除外（1,082件）
│
├── pipeline_log.txt             # パイプライン実行ログ（詳細・最新値はここ）
│
├── .env                         # APIキー（**git管理外**。IEEE / Scopus / Semantic Scholar）
├── .env.example                 # 変数名テンプレート（コミット可・値は空）
├── venue_aliases.csv            # 著者確認済みVenueエイリアス表（Phase 2 の最優先照合）
├── self_scale_references.csv    # ★正式 gold set（SearchScope列: in-scope 12件 / background 8件）
├── known_items.md               # 拡充用の下書き（現在は有効行0のテンプレート、下記注参照）
├── known_item_analysis.md       # ★自動生成: 脱落分析（known_item_test.py が書く）
├── README.md                    # このファイル
└── docs/                        # プロトコル文書（2026-07-21 集約）
    ├── rule.md                  # 研究プロトコル・方針文書（Rev.8/10/11 を本文へ反映済み）
    ├── protocol_changelog.md    # ★プロトコル変更履歴（〜Rev.13）— 方針の一次情報
    ├── PROGRESS_LOG.md          # ★進捗ログ（セッションログ・次回タスク）
    ├── methodology_decision_Rev7.md  # 検索方法論のデータ検証・確定（§Rev.8追記含む）
    ├── search_strings.md        # DB別検索式の記録（PRISMA Item #7）
    ├── search_replication.md    # 検索記録の復元・再実行手順
    ├── snowballing_protocol.md  # 引用探索による補完手続き
    └── normalization_design.md  # Venue正規化の設計案（案1〜6、未適用）
```

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
> **`rule.md` 本文への反映は第2波再検索の完了後にまとめて行う**予定（`docs/PROGRESS_LOG.md` の
> 「次回やること」）。それまでの間、方針の最新状態は `docs/protocol_changelog.md` を見ること。

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
> gold set 検証でスコア≤1の除外は **12件中3件（Being Barbie 含む）を落とす**。
> 理由は構造的で、(a) スコアは「関連性」ではなく「検索クエリと同じ語彙を使っているか」を
> 測っている（スケール知覚カテゴリのヒット率2.5%）、(b) 要旨欠落と交絡し、要旨なし文献の
> 95.1% がスコア1点以下になる。詳細は `docs/protocol_changelog.md` Rev.13。

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
> `docs/normalization_design.md` の6案（推奨: 案6 順序修正 + 案1 種別マーカー +
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

| 分類 | 件数 |
|---|---|
| CORE A/A* | 306件 |
| SJR Q1 | 838件 |
| エイリアス経由の通過 | 23件 |
| **通過合計** | **1,167件** |
| CORE 低ランク（B/C等） | 1,114件 |
| SJR Q2/Q3/Q4 | 860件 |
| ランク未判定（Unmatched） | 3,097件 |
| **除外合計** | **5,150件** |

> 入力は Phase 1.5 通過分の 6,317件。Rev.12 の正規化改修（種別マーカー・短キーガード・
> サニティチェック・照合順序の修正）が適用されており、`Match_Stage` 列でどの段で照合したかを追える。

> **Venue フィルタの取りこぼし（Threats に記載必須）:** Known-Item Test の in-scope 12件のうち
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
| **通過（最終候補）** | **784件** | **67.2%** |
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
├─ Phase 2 学会ランクスクリーニング ──── -5,150件
│   └─ 高ランク通過: 1,167 件
│
└─ Phase 3a キーワード除外 ──────────── -383件
    └─ 最終候補    : 784 件  ← step3_kw_included.csv（Phase 3b の対象）
```

**DB間重複の内訳（初回分、重複除去の報告用）:**
PubMed∩Scopus 606 / Scopus∩IEEE 352 / Scopus∩ACM 142 / PubMed∩IEEE 39 / ACM∩IEEE 0 / ACM∩PubMed 0
（`outputs/raw_db_audit.csv`）

### 検索の網羅性検証（Known-Item Test）

`scripts/known_item_test.py` が gold set（`self_scale_references.csv`、`SearchScope` 列で in-scope 12件）を
各 step ファイルに突き合わせ、recall を測定して `known_item_analysis.md` を生成する。

| 段階 | 生存 | recall |
|---|---|---|
| step0 統合生データ（検索式で拾えたか） | 8/12 | **66.7%** |
| step1 重複削除後 | 8/12 | 66.7% |
| step2 Venueランク通過後 | 3/12 | **25.0%** |
| step3 最終候補 | 3/12 | 25.0% |

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

> **注:** 本節の数値は旧データ（2026-05-25, 1,784件）時点の集計で**未更新**。現行データ（784件）での最新値は再実行が必要。

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
| 引用数 < 5 | 1,030件 | 754件 | 42.3% | 754件 |
| 引用数 < 10 | 1,030件 | 754件 | 42.3% | 754件 |
| 引用数 < 20 | 1,030件 | 754件 | 42.3% | 754件 |

> 引用数が全件不明（0扱い）のため、閾値によらず結果が一定（フェイルセーフ対象の754件 = 2023年以降のみ残存）。

**年代別内訳（引用数補完後の判定参考）:**

| 年代 | 件数 |
|---|---|
| 2023年以降（フェイルセーフ対象） | 754件 |
| 2022年以前（足切り対象になりうる） | 1,030件 |
| 発行年不明 | 0件 |

**発行年分布の概要（step3_kw_included.csv）:**

| 期間 | 件数 |
|---|---|
| 〜2014年 | 69件 |
| 2015〜2019年 | 300件 |
| 2020〜2022年 | 442件 |
| 2023〜2024年 | 430件 |
| 2025〜2026年 | 324件 |

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
| Cat1 VR環境 | 1,294件 | 72.5% | 検索クエリ由来のため高ヒット率 |
| Cat2 身体化 | 372件 | 20.9% | |
| Cat3 スケール知覚 | 61件 | 3.4% | **極めて低率 ← 要注意** |

> Cat3のヒット率が3.4%と著しく低い理由として、スケール知覚の記述が Abstract でなく Full-text に留まるケースが多い可能性がある。Abstract 欠損が550件（30.8%）存在する点も影響している。

#### スコア別 件数内訳

| スコア | 件数 | 割合 | 解釈 |
|---|---|---|---|
| **0点** | **409件** | **22.9%** | 全カテゴリ不一致 → 最優先除外候補 |
| **1点** | **1,048件** | **58.7%** | 1カテゴリのみ一致 → 除外候補 |
| **2点** | **302件** | **16.9%** | 2カテゴリ一致 → 要精査 |
| **3点** | **25件** | **1.4%** | 全カテゴリ一致 → コアトピック確定 |

#### スコア閾値別 足切りシミュレーション

| 足切り条件 | 除外件数 | 残存件数 | 残存率 |
|---|---|---|---|
| スコア < 1点を除外 | 409件 | 1,375件 | 77.1% |
| スコア < 2点を除外 | 1,457件 | 327件 | 18.3% |

#### タスク1A × 1B クロス集計マトリクス（引用数 < 5、フェイルセーフ適用）

|  | KW=0 | KW=1 | KW=2 | KW=3 | 合計 |
|---|---|---|---|---|---|
| 除外（引用数不足）| 293 | 568 | 155 | 14 | **1,030** |
| 残存（引用数OK）| 116 | 480 | 147 | 11 | **754** |

> 引用数OK（2023年以降）の中でもKW=1が480件と最多。これらは「VR環境」のみヒットしており、身体化・スケール知覚のキーワードを含まない → Phase 4 全文審査で慎重に評価すべき層。

---

### タスク 2: 取得元データベース集計

URL列のドメイン、DOIプレフィックス、Publisher列を優先順位付きで総合判定。

**判定優先順位:** URL内ドメイン → DOIプレフィックス → Publisher名

| データベース | 件数 | 割合 | 判定基準 |
|---|---|---|---|
| **ACM** | **654件** | **36.7%** | `dl.acm.org` / DOI `10.1145` |
| **IEEE** | **436件** | **24.4%** | `ieeexplore.ieee.org` / DOI `10.1109` |
| **Scopus/Elsevier** | **652件** | **36.5%** | `scopus.com` / `sciencedirect.com` / DOI `10.1016` |
| PubMed/PsycInfo | 0件 | 0.0% | `pubmed.ncbi.nlm.nih.gov` / DOI `10.1037` |
| Others/不明 | 42件 | 2.4% | 上記以外 |
| **合計** | **1,784件** | **100.0%** | |

> PubMed/PsycInfo が0件なのは、これらのデータベース由来の文献が Scopus/Elsevier 経由でインポートされ、
> URL が scopus.com になっているためと考えられる（**取得元DBの内訳は本集計ではなく
> `scripts/raw_db_audit.py` による `raw/` のDB別コレクション実測を正とする** — §6の内訳を参照）。

**Others/不明（42件）の内訳（DOIプレフィックス）:**

| DOIプレフィックス | 件数 | 出版社 |
|---|---|---|
| `10.1038` | 6件 | Nature Publishing Group |
| `10.3389` | 5件 | Frontiers in ... |
| （DOI無し） | 4件 | 不明 |
| `10.3390` | 3件 | MDPI |
| `10.1103` | 2件 | American Physical Society |
| その他 | 22件 | 各種 |

---

## 8. スノーボーリング（引用探索）

`scripts/snowball_search.py` — Semantic Scholar Graph API + Crossref による前方・後方引用探索の自動化。
手続きの定義は `docs/snowballing_protocol.md`、本節はその**実装**の説明。

> ⚠️ **外部APIに通信する**（Semantic Scholar / Crossref）。既定では著者が実行する。
> 2026-08-06 に著者の明示的な指示により初回実行済み。
> スクリプトが行うのは「取得」と「機械的に分かる情報の付与」までで、**PICOS採否は著者が判断する**。

### 8.1 なぜ必要か

Known-Item Test で、in-scope 12件中 **5件が Phase 2 の Venue ホワイトリストで脱落**していることが判明した
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
ホップ数は `docs/snowballing_protocol.md` §2.3 のとおり **2ホップまで**。**現在は1ホップのみ実施済み。**

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
> 表記ゆれがあると既出を見逃す。手作業での照合が必要（`docs/snowballing_protocol.md` §4.4）。

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
`docs/snowballing_protocol.md` §4（Mermaid 図あり）を正とする。

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
> `docs/PROGRESS_LOG.md` の方針に従うこと。

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
> 取り込んでから CSV エクスポートし `raw/` に置く運用（`docs/search_replication.md` Option A/B）。
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
これを下書きとして `docs/search_strings.md` の DB別記録表に verbatim で転記する。

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

## 11. 期待される知見と貢献

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
採用する場合は `docs/protocol_changelog.md` に改訂として記録すること
（Known-Item Test で recall への影響を測るのが前提）。

---

*最終更新: 2026-07-30（README全体の実装・方針との突き合わせ）｜プロトコル: PRISMA 2020 準拠（〜Rev.8）*