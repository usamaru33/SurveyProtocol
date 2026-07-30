# Protocol Changelog — プロトコル変更履歴

> システマティック・レビューのプロトコル(`rule.md`)に対する全変更を日付つきで記録する。
> ACM Computing Surveys の方法論セクション(protocol deviations の報告)に転用するため、
> 各項目は「変更内容 / 変更理由 / 影響範囲」を明記する。

---

## 2026-07-27 — Rev.8 補足: Scopus scope の実測とTA基準の再確認

`scripts/db_search_scopus.py`(Scopus Search API 自動検索ツール)の `--count-only` 実測により、
Rev.7以来「要著者確認」だった Scopus のフィールドscope(TITLE-ABS か TITLE-ABS-KEY か)に
高確度の証拠が得られた: 同一G1拡張クエリで `TITLE-ABS` = 2,533件、`TITLE-ABS-KEY` = 4,727件。
旧初回検索の記録値(4,331件)は拡張後 TITLE-ABS より多く TITLE-ABS-KEY と整合するため、
**旧検索は実際には TITLE-ABS-KEY で実行されていた可能性が高い**と判断(完全な証明ではない)。

**決定(著者確認):** Rev.7/8 の TA基準(TITLE-ABS)は変更しない。ただし
「TA基準は旧初回検索より実質的に狭い(同クエリで-46%)」ことを Threats to Validity に明記し、
索引語経由でのみ捕捉されていた文献の残余リスクはスノーボーリングで緩和する対象とする。
詳細は `methodology_decision_Rev7.md` §Rev.8「2026-07-27補足」、`search_strings.md` の
Scopus行を参照。影響範囲: 数値・実装は未変更(方針の再確認のみ)。

---

## 2026-07-22 — Rev.8: DB構成と検索scopeの最終確定(3DB体制)

> 詳細・PsycINFO正当化ドラフトは `methodology_decision_Rev7.md` §Rev.8 追記を参照。
> 著者確定事項であり、以後この方針で実装を進める(新規の方針議論はしない)。

### 確定: DB構成を4DBから3DBへ(ACM Digital Library + IEEE Xplore + Scopus)

- **PubMed は不使用に確定。** 理由: 医学・治療目的の文献は本サーベイのスコープ外であり、
  当該DBは主題適合性が低いため選定しない。Rev.7 の分析(known-item 固有寄与0・corpus固有175件)は
  参考情報として保存するが、不使用の決定はこの分析結果とは独立に行う
  (「Scopus で代替できるから外す」ではなく「主題的にそもそも選定基準を満たさない」が理由)。
- **PsycINFO はアクセス制約により利用不可(既存の事実、Rev.5時点で確定済み)。**
  Scopus が PsycINFO 収録誌の相当部分を索引しているため、心理学系文献の捕捉は Scopus に依拠する。
  この妥当性は Known-Item Test で実証済み: 心理系 #5(PLoS ONE)/ #6(PNAS)/ #14(Cognitive Processing)は
  いずれも Scopus で捕捉、#10 は **Scopus が唯一の捕捉源**(`outputs/known_item_test.csv` 実測、
  Rev.7 §B と同一データ)。残余リスク(Scopus固有では拾えない心理系文献)は
  `snowballing_protocol.md` のスノーボーリングで緩和する。

### 確定: 実効scope・フィルタ層・検証方針(Rev.7からの継続)

- 実効scope は **Title-Abstract(TA)を基準**。Scopus の Keyword が再取得できれば TA+K に格上げ可。
- フィルタ層は「レコードが持つ利用可能フィールドのみで判定+degradeフラグ」方式。PRISMA-S に明記。
- Known-Item Test 維持。目標 step0 ≥ 80%。現 69.2%(4DBデータでの測定値)は Rev.6 再検索後に再測定。
  ※3DB体制での再測定は、PubMed経由でのみ捕捉されていた known-item が無いこと(Rev.7 §B: PubMed固有寄与0)
  から、**recall には影響しない見込み**(要 Rev.6 再検索後の実測で確認)。
- Venue脱落分・学際文献はスノーボーリングで回収、PRISMA右カラムで報告(方針変更なし)。

### 既存文書への反映(削除ではなく無効化の記録)

- `search_strings.md` / `search_replication.md` の PubMed / PsycInfo 関連手順を
  「Rev.8 により不使用に確定」と明記(記述自体は経緯として残す)。
- `methodology_decision_Rev7.md` に Rev.8 追記セクションを新設。DB選定の最終構成・理由、
  PsycINFO 正当化ドラフト(Threats to Validity 転用可)、Rev.7 の PubMed 分析を
  「Rev.8 で3DBに確定したため参考情報」と注記。

### 影響範囲

- **実データ・step ファイルは未変更。** raw/PubMed.csv 等は経緯保存のため削除しない。
  PubMed を除いた3DB体制でのパイプライン再実行(統合データの再構築)は、
  Rev.6 第2波再検索・エクスポート欠陥是正(ACM Abstract / Scopus Keyword)と合わせて
  次の公式再実行時に反映する(本 Rev.8 は方針確定であり、再実行そのものは別タスク)。
- `outputs/pubmed_unique_175.csv` の30件 judge_relevance 判定タスクは、PubMed不使用確定により
  **優先度を格下げ**(参考記録として保持するが、DB選定の根拠には使わない)。

---

## 2026-07-21 — Rev.7: 検索方法論5方針のデータ検証と確定

> 詳細・一次証拠は `methodology_decision_Rev7.md`(A〜D の全数値)を参照。
> 検証は決定論的(DOI/正規化タイトル一致・列充足カウント)、LLM/API 不使用。既存 step ファイルは未変更。

### 判定サマリ(5方針)

- **方針1(4DB維持): 支持(条件付き)。** Scopus は known-item #10 の唯一の情報源、
  心理系 #5/#6/#14 を ACM/IEEE の代わりに捕捉(corpus固有 3,247件)→ 必須性を強く支持。
  一方 **PubMed の known-item 固有寄与は 0**(全 PubMed known-item は Scopus にも在る)。
  維持はするが corpus固有 175件・PsycInfo 未実行(心理系唯一の専門DB)・MeSH 潜在価値を根拠とし、
  「PubMed の正当化は現 known-item セットでは実証できていない」旨を本文に明記する。
- **方針2(実効scope を TAK 統一): 修正。** 列充足が非対称: **ACM の Abstract は 4.3%(342/7,997)**、
  usable な Keyword 列は **PubMed のみ**(MeSH 95%。ACM の Manual Tags は item-type 混入、Scopus 1.2%)。
  → 一律 TAK は現エクスポートでは不可能。**共通分母は Title(全DB 100%)**、Abstract は ACM で欠落、
  K は PubMed のみ、と正直に定義し直す。
- **方針3(フィルタ層で正規化クエリ再適用): 支持(要 degrade 設計)。** 4DB は Zotero 完全同一スキーマで
  再適用の枠組みは実装可能。ただし中身が非対称(方針2)のため、レコード単位で「利用可能フィールドのみ」で
  判定し degrade をフラグ化+PRISMA-S 明記する方式に限定して採用。
- **方針4(PubMed のみ MeSH 活用): 修正(格下げ・要データ)。** MeSH は Manual Tags に格納済み(95%)で
  post-hoc 利用可能だが、**known-item での恩恵=0**(step0 欠落4件は 3件が Frontiers VR=PubMed 非収載、
  1件 Being Barbie は PubMed raw 不在)。検索分岐の根拠が無いため「フィルタ層内の任意 recall ブースタ+
  PRISMA-S 報告項目」に格下げ。corpus 便益はライブ差分テスト待ち=判断保留。
- **方針5(Known-Item Test / step0≥80%): 支持(未達・セット要拡充)。** 方法論は支持。現 step0=69.2% で未達、
  セットは 13件(最低ライン)、心理接合点 seminal(Botvinick&Cohen 1998 / Lenggenhager 2007)未収録。
  Rev.6 再検索後の再測定+background known-item 追加が条件。

### 副次発見(数値上の支配要因)

Known-item 脱落の主因は検索段階でも DB 構成でもなく **Venue ホワイトリスト(CORE A\*/A + SJR Q1)**。
13件中 **6件が step2 脱落**(#3, #7, #8, #10, #13, #14)。Zhou et al. 2025 が「検索段階の学際取りこぼし」を
Limitations で自認したのに対し、本プロトコルは「厳格な venue フィルタが同じ取りこぼしを step2 で起こす」ことを
Known-Item Test で**定量化**できている点が優位。当該6件はスノーボーリングで回収し PRISMA 右カラムで報告する。

### 影響範囲

- 新規ファイル `methodology_decision_Rev7.md` を追加(実装・step ファイル・数値は未変更、分析のみ)。
- 未確定事項は同ファイル「著者に確認すべきこと」7項目・「判断保留・要データ」4項目として明示
  (PubMed固有175件の適合率、MeSH ライブ差分、ACM Abstract 再取得、Scopus Keywords 再取得、
  background known-item 追加、DB別 verbatim フィールド構文、known_items.md の正式化)。
- rule.md 本文の反映(方針2 の scope 定義修正、方針4 の MeSH 位置づけ、Threats への venue フィルタ取りこぼし)は
  上記データ確認の完了後に実施する(本 Rev.7 は方法論判定の確定まで)。

### Rev.7 実行分(2026-07-21・確定方針への是正タスク、外部通信/step ファイル変更なし)

Rev.7 判定を著者が確定(Scopus/PubMed 維持、scope は TA 基準、フィルタ層は degrade フラグ方式、
MeSH は格下げ、Known-Item Test 維持)。これを受け以下を整備:

- **エクスポート欠陥の是正手順**(§D 対応): `search_replication.md` に「Rev.7 エクスポート欠陥の是正」節を追加。
  ACM Abstract(4.3%)は Zotero/ACM DL 再エクスポート優先・不可時は `scripts/enrich_abstracts.py`
  (Crossref → Semantic Scholar で DOI ベース補完、**外部通信のため著者実行・コードのみ整備**)で fallback。
  Scopus Keyword(1.2%)は Author/Index Keywords を含む再エクスポート手順を明記。
  verbatim フィールド構文は `search_strings.md` に「Rev.7 運用ルール」(Scopus=TITLE-ABS / PubMed=[tiab] /
  ACM=Title:Abstract: / IEEE=Document Title:Abstract:)を第2波で必須記録として追加。
- **PubMed 固有 175件の適合率**(著者確認#1): `scripts/pubmed_unique_audit.py` を新規追加・実行。
  他DB(ACM/IEEE/Scopus/IEEE更新)に DOI・正規化タイトルとも不一致の **175件**を
  `outputs/pubmed_unique_175.csv` に出力(seed=42 の無作為30件に judge_relevance 空欄+MeSH・Abstract 抜粋)。
  適合率の推定手順を docstring に明記(判定は著者・LLM不使用)。
- **Gold set の一本化**(著者確認#7): 正式セットを `self_scale_references.csv` に確定。
  `known_items.md` 冒頭に位置づけ注記。心理接合点の古典 2件を **background** として追加
  (#19 Botvinick & Cohen 1998 / #20 Lenggenhager 2007。非VR・recall 分母外)。
- **Venue 脱落6件のスノーボーリング運用**(最重要発見への対処): `scripts/venue_dropped_audit.py` を
  新規追加・実行し `outputs/venue_dropped_known_items.csv` を生成(分類実測: unmatched 3 / below_rank 2 /
  criterion 1)。回収手順を `snowballing_protocol.md` に新規記述(シード選定・前後方探索・PICOS 採否・
  PRISMA 右カラム "citation searching" 計上、below_rank/criterion 別の扱い)。
- **影響範囲**: すべて分析・文書・補助スクリプトの追加。パイプライン数値・step ファイル・
  PRISMA 上段は不変(README 更新不要)。外部 API を叩くスクリプトは未実行(著者実行前提)。

---

## 2026-07-16 — Rev.2: AI判定の全面廃止と人手ダブルスクリーニングへの置換

### 変更 1: 「Phase 3: AI支援による要旨判定」を削除し、Phase 3a / 3b に置換

- **旧:** LLM(Google Gemini)による要旨判定。HCI分野は保守的戦略(再現率優先)、
  心理分野はPICOS厳格照合(適合率優先)として分野別に分岐。判定後に無作為抽出の目視確認。
- **新:**
  - **Phase 3a:** 決定論的キーワード除外(正規表現、実装済み `pipeline.py`)。
    全除外パターンの追加理由をPICOS基準と対応づけて rule.md に明記。
  - **Phase 3b:** Title/Abstract の人手二重スクリーニング
    (評価者2名・独立判定・Cohen's κ 報告・不一致は協議、未解決は Include 側へ)。
- **理由:** ACM CSUR の再現性要件。LLM判定は
  (a) モデルバージョン依存で第三者再現が不可能、
  (b) プロンプト感度の報告方法が確立していない、
  (c) PRISMA / Kitchenham 系ガイドラインに標準手続きが存在しない。
- **影響範囲:** step3_kw_included.csv(1,784件)までの既存出力は Phase 3a に相当し**変更なし**。
  Phase 3b は未実施であり、以降の件数はこの変更の影響を受ける。
  rule.md の分野別分岐(HCI/心理)は AI 戦略の差に由来していたため、廃止に伴い単一フローに統合。

### 変更 2: Phase 1 として「重複削除」を明文化

- **旧:** rule.md に重複削除の記載なし(実装 `pipeline.py` には存在)。
- **新:** DOI → Zotero Key → 正規化タイトルの優先順位による決定論的重複削除を Phase 1 として明記。
- **理由:** 実装とプロトコル文書の整合。PRISMAフロー図の "Duplicates removed" に対応する手続きの明文化。
- **影響範囲:** 手続き自体は実行済み(14,385 → 12,442件)。数値の変更なし。

### 変更 3: CORE ランク基準の表記修正

- **旧:** 「学会ランク(CORE Ranking等)A以上を採用」
- **新:** 「CORE Ranking **A\* または A** のみ採用」
- **理由:** 実装(`HIGH_RANKS = {"A*", "A"}`)との厳密な整合。「A以上」という表現の曖昧性排除。
- **影響範囲:** 実装は当初からこの基準。数値の変更なし。

### 保留(未確定): SJR「Q1原則・不足時のみQ2」と実装(Q1のみ)の乖離

- **状況:** rule.md は「Q1原則・不足時のみQ2まで採用」だが、実装は Q1 のみ採用。
- **証拠:** Q2により脱落したのは **823件/332誌**(`outputs/sjr_q2_excluded_venues.csv`)。
  上位は臨床系(Journal of Clinical Medicine 34件、Frontiers in Neurology 23件等、
  Phase 3a Cat3 でどのみち除外される層)と LNCS(131件)だが、
  **IEEE Transactions on Haptics(13件)、Computer Animation and Virtual Worlds(15件)、
  Multisensory Research(3件)、Quarterly Journal of Experimental Psychology(6件)、
  Neuropsychologia(5件)** など主題関連誌を含む。
- **決定事項(著者判断待ち):** 本文を「Q1のみ」に合わせるか、実装を「Q2まで」に広げるか。
  rule.md 該当箇所に TODO コメントを埋め込み済み。決定後、本ファイルに Rev.3 として記録すること。

---

## 2026-07-17 — Rev.3: IEEE 更新検索の統合(検索の修正)

### 変更: IEEE Xplore の更新検索(出版年 2025〜2026)を実行し、データセットに統合

- **背景:** 初回検索の実行時点が IEEE のみ 2025-12-25 で、他3DB(2026-05-15)より約5ヶ月古く、
  2026年前半の IEEE 文献(IEEE VR 2026 等)が捕捉されない非対称があった(raw_db_audit.py で発見)。
- **実施:** IEEE Xplore で出版年 2025〜2026 に限定した更新検索を実行(2026-07-17、**297件**)。
  既存14,385件とのDOI重複 196件、**真に新規 101件**。
  `ResearchVR3.csv`(14,385 + 297 = **14,682件**)を新たなパイプライン入力とし、重複は Phase 1 で除去。
- **結果(新旧比較):**
  | 段階 | 旧 | 新 | 差 |
  |---|---|---|---|
  | 元データ | 14,385 | **14,682** | +297 |
  | Phase 1 重複削除後 | 12,442 | **12,543** | +101 |
  | Phase 2 ランク通過 | 2,858 | **2,909** | +51 |
  | Phase 3 最終候補 | 1,784 | **1,827** | +43 |
- **PRISMA 報告:** IEEE の検索は2回(2025-12-25 初回、2026-07-17 更新)として報告する。
- **影響範囲:** step1〜3 の出力CSV・pipeline_log.txt を新数値で上書き。
  README の PRISMA 数値を更新(詳細表・§7は旧値のまま注記)。
  `outputs/sjr_q2_excluded_venues.csv` を再生成(Q2脱落 823→**826件**/332誌。Rev.2 の保留判断は継続)。

---

## 2026-07-17 — Rev.4: SJR 採用基準を「Q1のみ」に確定(Rev.2 保留事項の解決)

- **決定:** rule.md の「Q1原則・不足時のみQ2まで採用」を、実装どおり **「Q1のみ採用」に確定**(著者決定)。
- **理由:** 実装(pipeline.py)は当初から Q1 のみであり、既存の全スクリーニング結果と整合する。
  基準を単純かつ決定論的に保つことを優先。
- **認識済みの影響:** Q2除外は 826件/332誌。うち主題関連誌として IEEE Trans. on Haptics(13)、
  Computer Animation and Virtual Worlds(15)、Multisensory Research(3)、Cognitive Processing(5、
  Known-Item「Gulliver's virtual travels」の脱落を確認済み)等を含む。
  この影響は **Threats to Validity 節で明示的に報告**する(証拠: `outputs/sjr_q2_excluded_venues.csv`)。
- **影響範囲:** 実装・数値の変更なし(文書を実装に合わせた)。

## 2026-07-17 — Rev.5: 検索式の記録訂正(文書上のクエリ ≠ 実行クエリ)

- **発見の経緯:** Known-Item Test で「タイトルが文書上のクエリに完全適合するのに生データに不在」
  という矛盾を検出([9] eye height / self-avatars / virtual environments 論文)。著者確認の結果、
  **実際に実行された検索式は rule.md 旧版の記載と異なる**ことが判明。
- **実行された検索式(全DB共通・著者提供):**
  `("Virtual Reality" OR "VR" OR "HMD") AND ("Avatar" OR "Body" OR "Embodiment") AND ("Size" OR "Scale" OR "Height" OR "Distance")`
- **旧記載との差分:**
  - G1: "Virtual Environment" が**無い**(旧記載には有り)← 取りこぼしの主因
  - G2: "Body ownership"/"Virtual body" の複合語ではなく **"Body" 単独語**(広い)
  - G3: "Size perception" 等の複合語ではなく **"Size"/"Scale"/"Height"/"Distance" 単独語**(広い)
- **対応:** rule.md §3.1 を実行版に訂正し、旧記載が計画段階のものだった旨を注記。
  search_strings.md の verbatim 欄を記入。Known-Item Test の分析(コンセプト群判定)も実行版に更新。
- **含意:** G1 の狭さにより、"head-mounted display" / "immersive virtual environment" などの表現のみで
  VR を指す文献(例: Being Barbie, PLoS ONE 2011)が構造的に取りこぼされる。
  検索式改訂(G1 拡張)+ 再検索の要否が次の検討事項(Rev.6 候補)。

---

## 2026-07-17 — Rev.6: 検索式 G1 拡張と Venue フィルタ再設計(著者確定)

### 背景

Known-Item Test の in-scope recall が step0 69.2% / 最終 23.1% であり、
Kitchenham の quasi-gold standard 基準(step0 ≥ 80%)を満たさないため、
検索式と Venue フィルタの両方を改訂する。

### 変更 1: 検索式 G1 の拡張(スコープは変更しない)

- **新 G1:** `("Virtual Reality" OR "VR" OR "HMD" OR "head-mounted display" OR "head mounted display" OR "Virtual Environment*" OR "immersive virtual")`(G2/G3 は現行のまま)
- **理由(著者決定):**
  - "head-mounted display": VR の装置的定義。心理学系文献での慣用表現であり、
    同義語であってスコープ拡大ではない(例: Being Barbie は HMD を用いた VR 研究で
    スコープ内。脱落は著者が 'virtual reality' 語を title/abstract に用いなかったことによる
    検索式の再現率不足であって、スコープ違反ではない)
  - ハイフン無し表記("head mounted display"): DB間の正規化差異への対応
  - "Virtual Environment*": 再現率優先。非HMD系(CAVE等)の混入は Phase 3b の
    人手スクリーニングで除外可能であり、SLR の作法として検索段階では recall を優先する
  - "immersive" 単独は不採用: "immersive learning" 等の非VR文献を大量に拾い
    precision を著しく損なうため。"immersive virtual" に限定
- **状態:** 再検索は実施待ち。差分は第2波として PRISMA に報告する。

### 変更 2: Venue 照合をエイリアス表優先に再設計

- **新手順:** 著者確認済み `venue_aliases.csv` を CORE/SJR 照合より先に参照し、
  ファジーマッチを最後の手段に降格。エイリアス表は生文字列一致 → 正規化一致の2段で照合
  (正規化キーの同名衝突は警告のうえ exact 側のみで解決)。
- **是正された誤照合(現行データでの実測):**
  - 'Presence'誌 29件: CORE『Annual International Workshop on Presence』(C)への
    **正規化同名衝突による誤照合** → SJR Q3 に正規化。「ランク基準による除外」として記録
    (照合漏れによる除外と PRISMA 上区別)
  - 'ACM Transactions on Applied Perception'(TAP誌)49件: SAPシンポジウムとの
    正規化同名衝突で CORE B 誤照合 → SJR Q2 に正規化(基準による除外)
  - 旧称 'IEEE Virtual Reality Conference'(2007〜2011)の8件: 未照合で誤除外されていた
    **A* 論文を救済**(テスト実行で採用側に復帰することを確認)
- **試験実行(scratchpad、公式出力は未更新):** 14,682 → 12,543 → **2,917**(+8) → **1,831**(+4)。
  公式再実行は、著者によるエイリアス表確認と Rev.6 再検索データの統合後に行う。
- **注記(試験値の解釈について):** 上記の増分(2,909→2,917 / 1,827→1,831)は
  **第1波データ(旧クエリで取得)のみでの測定**である。Rev.6 クエリによる第2波データ投入後に
  再測定が必要であり、**この増分をもってエイリアス表の効果を評価してはならない**
  (第2波では対象レコードの構成が変わるため、増分は再現しない可能性が高い)。

### 自己申告: 従来監査(Task 4, 2026-07-16)の設計の穴

**2026-07-16 の「未照合5,126件監査」は未照合側のみを対象としており、
照合成功側の誤照合(false positive match)を検出できない設計だった。**
したがって当時の結論「A*/A/Q1 の表記ゆれ脱落 0件」は Venue フィルタ全体の妥当性を
保証しない。誤照合は Known-Item Test(Kilteni 2012 の誤除外)で初めて顕在化し、
本改訂で照合成功側の全数監査(`scripts/venue_match_audit.py`)を追加した。
実測: 非完全一致(acronym/fuzzy)照合が採否を左右したレコードは 1,183件
(採用側 590 / 除外側 593)、誤照合疑い 238ユニーク/707件
(`outputs/venue_suspect_matches.csv`、著者目視待ち)。

**追記(2026-07-17, 正規化同名衝突の全数監査):** `normalization_collision_audit.py` により
リスト内・リスト間の正規化同名衝突を全数検出した結果、**衝突キー899件**
(うち現行データに出現 133キー/489レコード)、**採否が変わる衝突 426件**(データ出現 74キー)。
Presence/TAP は氷山の一角であることが確定した。rank_conflict 全426件を venue_aliases.csv に
MANUAL 行として自動追記(著者確認待ち)。単一最大の誤照合は
`Proceedings of the ACM on Human-Computer Interaction`(SJR Q2 収載)の
CORE『Indian Conference on HCI』への fuzzy 誤照合(**82件** — CORE fuzzy が SJR exact より
先に走る段階順序が原因)。suspect の優先度付け(P1: 91ユニーク/240件、P2: 29/90、P3: 118/377)と
正規化関数の改善案は `normalization_design.md` を参照(実装は著者判断待ち)。

---

## 2026-05-25 以前 — Rev.1: 初版プロトコル

- rule.md 初版(検索戦略、AI支援スクリーニング、PICOS、Taxonomy 3軸)。
- `pipeline.py` による Phase 1〜3(現行番号で Phase 1 / 2 / 3a)を実装・実行
  (14,385 → 12,442 → 2,858 → 1,784件)。
