# Protocol Changelog — プロトコル変更履歴

> システマティック・レビューのプロトコル(`rule.md`)に対する全変更を日付つきで記録する。
> ACM Computing Surveys の方法論セクション(protocol deviations の報告)に転用するため、
> 各項目は「変更内容 / 変更理由 / 影響範囲」を明記する。

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
