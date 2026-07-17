# サーベイ進捗ログ — VR自己スケール知覚 システマティック・レビュー

> このファイルは作業再開時に「今どこまで終わっているか」を思い出すためのログ。
> 作業セッションごとに末尾へ追記していく。プロトコル本文は `rule.md`、実装詳細は `README.md` を参照。

---

## プロジェクトの骨子（30秒で思い出す用）

- **テーマ:** VR空間における自己スケール感覚（Self-scale perception）の形成要因の体系化。
  「視覚情報の支配的影響」と「非視覚的情報（聴覚・触覚）の構造的欠落」を定量的に示すのが狙い。
- **手法:** PRISMA 2020 準拠のシステマティック・レビュー。
- **RQ:** ①検討されてきた感覚モダリティの定量把握 ②介入(IV)と評価指標(DV)の構造的乖離
  ③視覚単独操作の知覚的限界（ミニチュア効果等） ④MLEモデルに基づく多感覚統合の理論的考察
- **分類3軸:** 介入モダリティ（Uni/Multi 2-way/3-way+）× 評価志向（Self/World/Ambiguous）× 知覚支配（Stimulus-Overriding / Context-Dominant / Conflict-Threshold）

---

## タイムライン

| 日付 | 出来事 |
|---|---|
| 2026-05-19 | リポジトリ作成・初回コミット（プロトコル文書、生データ、パイプライン一式） |
| 2026-05-25 | README.md 作成（パイプライン実装ドキュメント）。Phase 1〜3 実行済み・結果確定 |
| 2026-05-25以降 | `year_distribution.py` / `year_distribution.png` 追加（未コミット） |
| 2026-05-27 | 別プロジェクト `../docs-system`（Next.js 文献ブラウザ）を作業 |
| 2026-07-16 | 約1.5ヶ月ぶりに再開。本ログと Claude Code skills を整備 |

---

## 完了していること

### 1. 検索・データ収集
- ACM DL / IEEE Xplore / PubMed / Scopus で統合クエリ検索を実行し、Zotero 経由でエクスポート。
- 生データ: `ResearchVR2.csv`（**14,385件**）。

### 2. スクリーニング Phase 1〜3（`pipeline.py` 実行済み）

```
14,385 件（生データ）
  → Phase 1 重複削除（DOI/Key/Title）      : -1,943 → 12,442 件（step1_dedup.csv）
  → Phase 2 Venueランク（CORE A/A*・SJR Q1）: -9,584 →  2,858 件（step2_rank_included.csv）
  → Phase 3 キーワード除外（AR/技術論文/臨床）: -1,074 →  1,784 件（step3_kw_included.csv ★最終候補）
```

- 実行ログ: `pipeline_log.txt`（除外キーワードごとの件数内訳あり）

### 3. 追加分析（`simulate_screening.py`、読み取り専用）
- **タスク1A（引用数足切り）:** CSVに引用数列が無いため最悪ケースのみ。2023年以降のフェイルセーフで754件残存。→ 引用数の外部取得が必要（未着手）
- **タスク1B（KWスコア足切り）:** 3カテゴリスコアで 0点=409件 / 1点=1,048件 / 2点=302件 / 3点=25件。Cat3（スケール知覚KW）ヒット率が3.4%と極端に低い（Abstract欠損 550件=30.8% の影響大）
- **タスク2（DB別集計）:** ACM 654 / IEEE 436 / Scopus系 652 / その他 42。PubMed/PsycInfo表記は0件（Scopus経由で吸収されたと推定）

### 4. 年次分布の可視化（`year_distribution.py`）
- `year_distribution.png` 生成済み（総計・DB別積み上げ・DB別折れ線）。**未コミット**。
- 傾向: 2020年以降が急増（2020-22: 442件、2023-24: 430件、2025-26: 324件）。

### 5. 関連ツール `../docs-system`（Next.js、別リポジトリ相当）
- Semantic Scholar 検索 → 引用ネットワーク可視化（D3）→ Supabase 保存 + R2 にPDF保存、CORE/SJR ランク付与、という文献ブラウザを実装中。
- サーベイ本体との接続（1,784件の取り込み等）はまだ。`../DocsSystem` は空フォルダ（廃棄した試作跡）。

---

## まだやっていないこと（rule.md のプロトコルとの差分）

1. **Phase 3b: Title/Abstract 人手二重スクリーニング** — 評価者2名・独立・Cohen's κ 報告・不一致協議。**未実施**。
   - （旧計画の LLM 要旨判定は 2026-07-16 のプロトコル改訂 Rev.2 で廃止。protocol_changelog.md 参照）
1.5. **検索の再実行（PRISMA上段の再構築）** — DB別 verbatim 検索式・実行日・ヒット数が未記録のため、
   `search_replication.md` の手順で全DB再検索が必要。DB別生データを `raw/` に保全すること。
2. **引用数の補完** — Semantic Scholar API で DOI → citationCount を取得し CSV に列追加（README末尾にコード例あり）。足切りシミュレーションの実質化に必須。
3. **AI判定の目視検証** — 無作為抽出サンプルの著者チェック（rule.md 記載の信頼性担保手続き）。
4. **Phase 4: 全文適格性評価** — PICOS基準（健常成人 / HMD+スケール操作 / 比較条件 / 定量指標 / 実証研究）での全文精査。
5. **Taxonomy コーディング** — 採択文献への3軸分類の付与。
6. **分析・考察** — 年代×Taxonomy変遷、Venue別トレンド、タスク×モダリティのクロス集計、非視覚パラメータ体系化、Social VR・個人差の観点（rule.md §4）。
7. **PRISMA フロー図の作成**、rule.md 冒頭の「○○件」の確定値への置換。

## 既知の課題・メモ

- **Abstract欠損が30.8%（550件）** — KWスコアやLLM判定の精度に直結。Crossref/S2 APIでのAbstract補完を検討。
- **Phase 2 の未判定（Unmatched）5,126件をまとめて除外している** — 2026-07-16 に上位50 Venue（2,152件=42.0%をカバー）を監査した結果、Levenshtein類似度0.85以上で A*/A/Q1 に一致する「表記ゆれ脱落」は **0件**（`outputs/unmatched_venues_top50.csv`）。上位は VRCAI/VRIC 系 proceedings・CHI Extended Abstracts・Venue名空欄(233件) が中心。残り58%のロングテールは未監査。
- **rule.md と実装の乖離（SJR Q2）— 判断待ち:** Q2による脱落は **823件/332誌**（`outputs/sjr_q2_excluded_venues.csv`）。上位は臨床系＋LNCSだが、IEEE Trans. on Haptics(13)・Computer Animation and Virtual Worlds(15)・Multisensory Research(3)・QJEP(6)・Neuropsychologia(5) 等の主題関連誌を含む。rule.md 該当箇所に TODO 埋め込み済み。決定後 protocol_changelog.md に Rev.3 として記録する。CORE 側は「A*/A のみ」で rule.md を実装に合わせて確定済み（Rev.2）。
- **KW=1点の残存層480件（2023年以降）** — VR環境KWのみヒット。Phase 4 で要注意層。
- Windows での実行は `python -X utf8` を付けること（文字化け防止）。

---

## セッションログ（新しいものを下に追記）

### 2026-07-16
- 約1.5ヶ月ぶりの再開。リポジトリ全体を棚卸しして本ログ（PROGRESS_LOG.md）を作成。
- Claude Code 用 skills（survey-resume / survey-pipeline / survey-log）を `../.claude/skills/` に作成。
- 次のアクション候補（優先度順）を策定:
  1. 引用数・Abstract の API 補完（Semantic Scholar）
  2. LLM要旨スクリーニング（rule.md Phase 3）の実装・実行
  3. 目視検証 → Phase 4 全文評価へ
- 未コミットの `year_distribution.py` / `.png` と本ログのコミット推奨。

### 2026-07-16 (2) — Known-Item Test 基盤の整備(ACM Computing Surveys 投稿準備)
- **方針決定: 包含/除外判定に AI/LLM を使わない(再現性要件)。全スクリーニング基準は決定論的とする。**
  rule.md の「Phase 3: AI支援による要旨判定」は本方針に合わせて再設計が必要(rule.md 未修正、要対応)。
- `known_items.md` 作成 — quasi-gold standard テンプレート(目標15〜25件、Kitchenham 最低10件)。**著者の記入待ち。**
- `scripts/known_item_test.py` 作成 — 既知文献の step0〜3 生存判定。DOI→正規化タイトル→Levenshtein≥0.9(候補提示のみ、自動確定なし)。
  出力: `outputs/known_item_test.csv` + `known_item_analysis.md`(脱落分析レポート自動生成) + recall サマリ。
  実在論文6件でE2E検証済み(step0脱落/step2未照合/step2 Q2/step3誤爆/FUZZY の全経路動作確認、テストデータは削除済み)。
- `scripts/unmatched_venue_audit.py` 作成・実行 — Venue未照合 5,126件(ユニーク1,813種)の上位50件を監査。
  **結果: 表記ゆれによる高ランク(A*/A/Q1)脱落は0件**(上位50=2,152件、全体の42.0%)。→ Threats to Validity の証拠として `outputs/unmatched_venues_top50.csv` を使用可。
  - 特記: CHI Extended Abstracts 系が変種合計で約190件。EA≠フルペーパーなので除外維持が妥当だが、意図的判断として本文に明記すること。
  - 特記: Venue名空欄が233件(未照合の4.5%)。別途原因調査の価値あり。
- 制限事項の記録: DB別の統合前生データは保存されておらず(`Library Catalog` 列も全件空)、step0 は統合後 `ResearchVR2.csv` での存在判定+URL/DOIからのDB推定となる。
- skills を `.claude/skills/`(リポジトリ内)へ移動し git 管理下に。
- **次回やること(優先度順):**
  1. known_items.md に15〜25件を記入(Intro/RW/Taxonomy の引用予定から逆算、境界事例も含める)
  2. `python -X utf8 scripts/known_item_test.py` を実行し、known_item_analysis.md の脱落分析に基づき検索式/ホワイトリスト/除外KWを修正
  3. step2 Q2 脱落が出た場合、rule.md「Q1原則・不足時Q2」と実装「Q1のみ」の乖離をどちらに寄せるか決定
  4. rule.md の Phase 3(AI判定)を決定論的手法へ書き換え

### 2026-07-16 (3) — プロトコル改訂 Rev.2 と検索記録の現状把握
- **rule.md 改訂(Rev.2)**: 「Phase 3: AI支援による要旨判定」を削除し、
  Phase 3a(決定論的キーワード除外・全パターンの追加理由をPICOS対応表で明記)+
  Phase 3b(人手2名独立のTitle/Abstract二重スクリーニング・Cohen's κ 報告・不一致協議)に置換。
  HCI/心理の分岐フローは AI 戦略差に由来したため単一フローに統合。
  重複削除を Phase 1 として明文化、CORE「A以上」→「A*/A のみ」に表記確定。
  変更履歴は `protocol_changelog.md` に記録(CSUR 方法論セクション用)。
- **SJR Q2 乖離の判断材料を出力(判断は保留・TODO埋め込み済み)**:
  Q2脱落 = **823件/332誌**、全リスト `outputs/sjr_q2_excluded_venues.csv`。
  臨床系(Cat3でどのみち除外)+LNCS(131)が主だが、IEEE Trans. on Haptics(13)、
  Computer Animation and Virtual Worlds(15)、Multisensory Research(3)、QJEP(6)、Neuropsychologia(5) など主題関連誌あり。
- **検索記録の現状把握(結論: 全滅)**: 4DB すべてで verbatim 検索式・実行日・DB別ヒット数が未記録。
  PsycInfo は実行有無自体が不明。統合CSVに取得元DB列なし(URL/DOIによる出版社推定:
  ACM 8,345 / Scopus系 3,475 / IEEE 1,913 / 不明 650 / PubMed 2 — PRISMA報告には使用不可)。
- `search_strings.md` 作成(記録表テンプレート+現状の判明分+REQUIRES RE-RUN 明記)。
- `search_replication.md` 作成(DB別の検索構文・エクスポート形式・文字コード・上限・ID列・
  統合時のDB間/DB内重複の区別、再実行後チェックリスト)。
- **次回やること(優先度順):**
  1. SJR Q2 の扱いを確定(outputs/sjr_q2_excluded_venues.csv を目視)→ rule.md の TODO 解消 + changelog Rev.3
  2. known_items.md 記入 → Known-Item Test 実行(検索再実行の前に現行データで一度回し、検索式改訂の要否も判断)
  3. search_replication.md の手順で全DB再検索(同日実行・DB別生データを raw/ に保全・Source_DB列付与)
  4. 再検索データでパイプライン再実行 → PRISMA フロー図を上段から再構築

### 2026-07-16 (4) — 訂正: 検索データは Zotero でDB別コレクション管理されていた
- 著者より: 検索結果は Zotero で管理し、**取得元DB(ライブラリ)ごとにフォルダ分けしている**。
  リポジトリの CSV はその統合エクスポート。→ **「全DB再検索が必要」という (3) の結論を訂正**。
- `Date Added` 分析: 取り込みは **2025-12-25(1,276件)/ 2026-05-15(13,109件)の2波**。
  検索実行日の上限近似として使用可(2波の経緯は要著者確認)。
- `search_replication.md` を再構成: **Option A = Zotero コレクション別エクスポートによる復元(推奨・再検索不要)**、
  Option B = 再検索(verbatim 検索式の確定が必要な場合のみ)。search_strings.md も同様に更新。
- 依然として欠けるのは **verbatim 検索式・使用フィルタ**のみ(Zotero に保存されない情報)。
- **著者への依頼事項:**
  1. Zotero の各DBコレクションを CSV エクスポートして `SurveyProtocol/raw/` に保存
     (ファイル名: `<db>_zotero_YYYYMMDD.csv`)+ コレクション別件数を search_strings.md に記入
  2. 検索式の手元記録(メモ・DBアカウントの検索履歴等)の有無を確認
  3. 2025-12-25 と 2026-05-15 の2回取り込みの経緯(予備検索+本検索?追加DB?)を教える

### 2026-07-17 — PRISMA 上段の確定(raw/ 提供を受けて)
- 著者が `raw/` に Zotero コレクション別エクスポート4本を配置(acm/ieee/PubMed/Scopus)。
- `scripts/raw_db_audit.py` 作成・実行(`outputs/raw_db_audit.csv`):
  - **Records identified 確定: ACM 7,997 / IEEE 1,276 / PubMed 781 / Scopus 4,331 = 計 14,385**
  - 統合CSVと Zotero Key で **1:1 完全一致**(欠落・混入・複数コレクション所属 すべて0件)→ 統合エクスポートの完全性を確認
  - **2波の経緯が判明: 2025-12-25 = IEEE のみ / 2026-05-15 = ACM+PubMed+Scopus**
  - DB間重複: PubMed∩Scopus 606 / Scopus∩IEEE 352 / Scopus∩ACM 142 / PubMed∩IEEE 39 / ACM∩IEEE 0 / ACM∩PubMed 0
  - **PsycInfo は未実行が確定**(コレクション無し)。不実行判断の理由を本文に書く必要あり
- `scripts/known_item_test.py` を拡張: step0 で **どのDBコレクションが既知文献を捕捉したか**を
  `step0_source_dbs` 列に出力(raw/ 存在時のみ)。スモークテスト済み(例: IEEE VR 2018 論文 → 'ieee; Scopus')
- search_strings.md に確定値を記入(残りの未記録は verbatim 検索式・フィルタのみ)
- **新たな課題: 検索時点の非対称** — IEEE のみ 2025-12 実行で他DBより約5ヶ月古い。
  IEEE の更新検索(差分追加)か Threats to Validity 明記かの判断が必要
- **次回やること(優先度順):**
  1. SJR Q2 の扱いを確定(前日から継続、outputs/sjr_q2_excluded_venues.csv)
  2. IEEE 検索時点の非対称への対応方針を決定(更新検索 or Threats 明記)
  3. verbatim 検索式の手元記録を確認(無ければ Option B で該当欄のみ確定)
  4. known_items.md 記入 → Known-Item Test 実行

### 2026-07-17 (2) — IEEE更新検索の統合(Rev.3)と Known-Item Test 初回実行
- **IEEE更新検索を統合**: `raw/IEEE_2025-2026.csv`(297件、出版年2025:201/2026:96)。既存とDOI重複196、**新規101件**。
  `ResearchVR3.csv`(14,682件)を新入力としてパイプライン再実行:
  **14,682 → 12,543(-2,139) → 2,909(-9,634) → 最終候補 1,827件(+43、全てIEEE分)**。
  README・search_strings.md 更新、protocol_changelog.md に Rev.3 記録。検索時点の非対称は解消。
  year_distribution.png・outputs/sjr_q2_excluded_venues.csv(Q2脱落 826件/332誌に微増)を再生成。
- **Known-Item Test 初回実行**(`self_scale_references.csv`、18件。スクリプトは列エイリアス・--items・
  最新 ResearchVR*.csv 自動選択に対応拡張):
  - **recall: step0 50%(9/18)→ step2 16.7%(3/18)→ 最終 16.7%(3/18)**
  - **発見1(検索式のギャップ)**: 多感覚系の必須文献4件(footsteps音・action sounds・audio-tactile・足裏振動)が
    step0 で全滅。G3(スケール知覚語)に body weight/height, arm dimension 等が無く、非VRの心理実験は G1 も不成立。
    Being Barbie(原典)も脱落(タイトルに VR 語なし。G1 に "head-mounted display"/"immersive" が無い)。
  - **発見2(実行検索式への疑義)**: 「The effects of eye height and self-avatars on distance estimation in
    virtual environments」はタイトルだけで3コンセプト群すべて命中するのに生データに不在
    → 実際に実行された検索式が文書化クエリと異なる疑い。verbatim 検索式の確認が急務。
  - **発見3(Venueスクリーニングの実害)**:
    - Kilteni 2012(SoE定義・必須)が「Presence 誌 → CORE『Annual International Workshop on Presence』(C)」への
      **誤照合**で除外(同誌の誤照合は本体データで29件)。なお Presence:TVE は SJR Q3 のため正しく照合しても現基準では除外
      → 分野の歴史的中核誌がランク基準で落ちる構造問題。
    - Gulliver's virtual travels が Cognitive Processing **Q2** で脱落 → Q2判断に実害の証拠。
    - APGV/MIG/ACM ICPS の3件が Venue 未照合で脱落(ロングテール未照合にも関連文献が実在)。
  - 書籍(Gallagher 2005)・非VR理論(Tsakiris 2010)の step0 脱落は想定内(検索対象外)。
    known_items の「検索で拾えるべき群」と「手動追加の背景文献群」を分ける列の追加が必要。
- **次回やること(優先度順):**
  1. **検索式の再設計判断**: G1 に "head-mounted display"/"immersive"、G3 に body weight/height,
     arm/limb dimension, body representation 等の追加を検討(known_item_analysis.md の提案参照)→ 追加時は再検索
  2. **SJR Q2 の確定**(Gulliver 脱落という実害が判明。Q1+主題直結Q2誌の個別採用が有力)
  3. Venue誤照合(Presence 29件)への対処: CORE照合のファジー閾値/頭字語処理の見直し、または例外表
  4. self_scale_references.csv に「検索スコープ内/外」列を追加し recall を層別に再計算

### 2026-07-17 (3) — SJR Q1のみ確定(Rev.4)・実行検索式の判明(Rev.5)・脱落原因の完全分離
- **SJR は「Q1のみ」で著者決定(= A案)** → rule.md の TODO 解消、changelog Rev.4。
  Q2脱落(826件/332誌、Gulliver 論文含む)は Threats to Validity で報告する方針。実装・数値の変更なし。
- **実行された検索式が判明(著者提供)**:
  `("Virtual Reality" OR "VR" OR "HMD") AND ("Avatar" OR "Body" OR "Embodiment") AND ("Size" OR "Scale" OR "Height" OR "Distance")`
  → rule.md 旧版の詳細クエリは**計画段階のもので実行されていなかった**(Rev.5 で記録訂正)。
  実行版は G2/G3 が広く(単独語)、**G1 に "Virtual Environment"/"head-mounted display"/"immersive" が無い**。
  前回の「実行検索式への疑義」はこれで解決。
- **known_item_test.py を実行版クエリに更新**し、self_scale_references.csv に `SearchScope` 列を追加
  (background=書籍・非VR理論/心理5件は recall 分母から除外)。**in-scope recall: step0 69.2%(9/13)→ 最終 23.1%(3/13)**
- **step0 脱落4件の原因を完全分離**:
  - **DBカバレッジ欠落(3件)**: [9][12][18] すべて **Frontiers in Virtual Reality** 掲載。
    [9] はタイトルが実クエリに完全適合するのに不在 → 検索対象DBが同誌を索引していないことが確定。
    **同誌は SJR Q1** なので、捕捉できれば Phase 2 も通過し最終候補まで残れる。
  - **クエリG1ギャップ(1件)**: Being Barbie(PLoS ONE = Scopus/PubMed 索引済み・SJR Q1)。
    ライブラリ追加では直らず、**G1 拡張("head-mounted display"/"immersive"等)+再検索が必要**。
- **次回やること(優先度順):**
  1. **検索改訂 Rev.6 の実行判断(著者)**: (i) G1 拡張クエリで全DB再検索(第2波)、
     (ii) Frontiers in Virtual Reality のカバレッジ確保(Scopusの索引状況確認 or 誌内検索を
     supplementary source として追加、PRISMA の Other sources 行で報告)
  2. Venue誤照合(Presence→COREワークショップ、29件)と未照合3件(ACM ICPS/APGV/MIG)への対処
     (エイリアス表 or 例外表。Presence:TVE は SJR Q3 のため救済しても現基準では除外という論点も記録)
  3. Phase 3b(人手二重スクリーニング)の準備(データセットが検索改訂で動くため、Rev.6 確定後に着手)

### 2026-07-17 (4) — Rev.6 実装: G1拡張・Venue照合の再設計・誤照合監査
- **著者確定(Rev.6)**: 検索式 G1 を拡張(+"head-mounted display"/"head mounted display"/
  "Virtual Environment*"/"immersive virtual"。"immersive"単独は precision 悪化のため不採用)。
  スコープ不変。rule.md §3.1・search_strings.md に反映。**再検索は実施待ち**。
- **誤照合監査(`scripts/venue_match_audit.py` 新規・実行済み)**:
  - 照合成功7,377レコードの全数を段階別に再導出: SJR exact 3,137 / CORE exact 2,525 /
    **CORE fuzzy 966 / SJR ISSN 532 / CORE acronym 217**
  - **非完全一致が採否を左右: 1,183件(採用590/除外593)**。誤照合疑い 238ユニーク/707件
    → `outputs/venue_suspect_matches.csv`(著者目視待ち)
  - Presence 誤照合の正体は fuzzy ではなく**正規化同名衝突(exact_norm)**と判明
    → fuzzy 監査では原理的に検出不能なタイプ
- **監査設計の穴を changelog に自己申告**: 2026-07-16 の Task 4 監査は未照合側のみ対象で、
  誤照合(false positive)は検出できていなかった。「A*/A/Q1脱落0件」は Venue フィルタ全体の
  妥当性を保証しない。
- **`venue_aliases.csv` ドラフト作成(著者確認待ち)+ pipeline.py をエイリアス最優先に改修**
  (生文字列一致→正規化一致の2段。正規化キー衝突は警告して exact 側で解決):
  - Presence誌29件: CORE C 誤照合 → SJR Q3(基準による除外)に是正
  - **新発見: TAP誌(ACM Transactions on Applied Perception)49件が SAP シンポジウムとの
    正規化同名衝突で CORE B 誤照合** → SJR Q2 に是正(基準による除外)
  - **旧称 IEEE Virtual Reality Conference(2007〜2011)の8件を A* として救済**
  - scratchpad での試験実行: 2,909→**2,917**(+8)、最終 1,827→**1,831**(+4)。
    **公式の step ファイルは未更新**(エイリアス表の著者確認+Rev.6再検索データ統合後に公式再実行)
- Frontiers in VR の supplementary source 手順を search_replication.md に追加
  (Scopus索引確認 → 無ければ誌内検索、PRISMA "other methods" 行で報告)。
- **次回やること(優先度順):**
  1. **著者**: venue_aliases.csv の目視確認(特に「著者確認待ち」行)+
     outputs/venue_suspect_matches.csv(238ユニーク)の確認
  2. **著者**: Rev.6 クエリで全DB再検索(第2波)+ Scopus の Frontiers in VR 索引確認
     → raw/ に第2波エクスポートを配置
  3. 第2波統合 → エイリアス有効で公式パイプライン再実行 → 全数値更新
  4. **Task 4: known_item_test.py で recall 再測定(目標: step0 in-scope ≥ 80%)**
  5. ICPS(46件)の個別解決(ISBN/Extra列から会議名復元)は優先度低として保留

### 2026-07-17 (5) — 正規化同名衝突の全数監査・suspect優先度付け・正規化設計文書
- **`scripts/normalization_collision_audit.py` 新規・実行**(公式stepファイルは不変更):
  - CORE∪SJR のキー空間を pipeline と同一手順で再構築し、同名衝突を全数列挙:
    **衝突キー899件**(現行データ出現 133キー/489レコード)、
    **採否が変わる衝突(rank_conflict)426件**(データ出現 74キー)
    → `outputs/normalization_collisions.csv` / `collisions_rank_conflict.csv`
  - rank_conflict 全426件を venue_aliases.csv に MANUAL 行として**自動追記**(冪等・著者確認待ち)
  - 実例: `sensors`(Sensors Q1 vs Journal of Sensors Q2、19件)、`ieee multimedia`
    (Trans. Q1 vs Symposium CORE C、10件)、`psychological research`(Q1 vs Q3、6件)等
  - 限界を文書化: データ側の短い誌名×リストエントリ型(Presence型)はリスト内衝突として
    現れないため本監査対象外 → venue_match_audit の P2 で捕捉
- **suspect 238ユニークに優先度付与**(venue_match_audit.py 拡張・再実行):
  **P1(採否が変わり得る)91ユニーク/240件**、P2(別会場疑い)29/90、P3(表記ゆれ)118/377。
  P1 最大は `Proceedings of the ACM on Human-Computer Interaction`(**82件**)が
  CORE『Indian Conference on HCI』に fuzzy 誤照合 — SJR に Q2 で正確に収載されているのに
  **CORE fuzzy が SJR exact より先に走る段階順序**が原因(新発見の設計問題)
- **`normalization_design.md` 作成**(提案のみ・実装保留): 現行正規化仕様の明文化、
  衝突原因5類型+段階順序問題の特定、改善案6件のトレードオフ表、
  エイリアス表 vs 正規化修正の議論(多層防御を推奨: 案6順序修正→案1種別マーカー+
  案3短キーガード→案4サニティチェック+エイリアス表+監査常設)
- changelog に Task C 注記(Rev.6 試験値は第1波のみの測定であり、エイリアス表の効果評価に
  使ってはならない)と衝突監査の追記を記録
- **次回やること(優先度順):**
  1. **著者**: normalization_design.md の採否判断(推奨: 案6+案1+案3+案4)と閾値決定
  2. **著者**: outputs/venue_suspect_matches.csv の P1(91件)から目視。
     venue_aliases.csv の自動追記426行は P1/HIGH 優先で確認
  3. **著者**: Rev.6 クエリで全DB再検索(第2波)+ Frontiers in VR の Scopus 索引確認
  4. 第2波統合 + 正規化改修(著者決定後)+ エイリアス確定 → 公式再実行(Rev.7)
     → known_item_test で recall 再測定(目標 step0 ≥ 80%)
