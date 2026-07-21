## 1. 概要

本研究では、VR・HCI分野における主要な文献データベースである ACM Digital Library および IEEE Xplore, 心理・医学分野における主要な文献データベースである PubMed, Scopus から抽出された合計 ○○件 の文献候補に対し、多段階のスクリーニング及び分類を実施し、その後結果から多角的な視点で考察を行う。

## 2. 本調査の目的とRQ

### 2.1 調査の目的

本システマティック・レビューの主たる目的は、VR空間における自己スケール感覚（Self-scale perception）の形成に関わる諸要因を網羅的に体系化し、現在の研究領域における「視覚情報の支配的影響」と「非視覚的情報の構造的欠落」を定量的な事実として提示することである。

具体的には、既存の実証研究を「介入モダリティ」「評価対象（自己対環境）」「理論的枠組み」の三軸で構造化し、視覚主導のスケーリング操作が抱える知覚の帰属先に関する「尺度の曖昧性」を特定する。これにより、身体運動に随伴する聴覚・触覚フィードバック（接地音や足裏振動）が、自己スケールの確定および「身体化のもっともらしさ」を担保する上で果たす理論的役割を導出することを最終的な目的とする。

### 2.2 RQ

本調査では、VR空間設計における多感覚統合による新たな身体表象モデルを探求するため、以下の4つのリサーチクエスチョン（RQ）を設定する。(3,4は仮決め)

- **RQ1: 自己スケール感覚の形成において、現在までにどのような感覚モダリティが検討されてきたか？**
    - 視覚操作（アイレベル、アバタサイズ、局所的変形など）以外の非視覚的要因（聴覚、触覚、運動同期）が、実証研究においてどの程度扱われているかを定量的に明らかにする。
    - HCIと心理系の違うところ、似ているところも
    - 心理がどのようにして入ってきたか、分野がどのように統合されてきたか
- **RQ2: 介入手法（独立変数）と評価指標（従属変数）の間にどのような構造的乖離が存在するか？**
    - 「自己の身体図式の更新」を意図した介入に対し、評価系が依然として「外界のサイズ・距離判断（World-scale）」という外的尺度に依存している現状を分析し、それが知覚の曖昧性に与える影響を特定する。
- **RQ3: 視覚的なスケーリング操作単独では、どのような知覚的限界や錯誤が生じるか？**
    - 極端な倍率操作（巨大化・縮小化）において、脳が「自己の変容」ではなく「環境の変容（ミニチュア効果など）」を選択する境界条件や、知覚の飽和点に関する既存の知見を整理する。
- **RQ4: 多感覚統合モデルは、自己スケール感覚の確定においてどのように機能し得ると理論づけられるか？**
    - 最尤推定（MLE）モデルに基づき、視覚情報の不確実性が高まる条件下において、行動随伴的な聴覚・触覚情報がいかに「絶対的尺度」として信頼性加重を高め、知覚を自己側へ定着させるかを理論的に考察する。

---

## 3. 調査手法 (Search and Analysis Methodology)

本研究では、VR空間における自己スケール感覚の形成要因を網羅的に特定し、そのトレンドと未開拓領域を解明するため、**PRISMA 2020声明 (Preferred Reporting Items for Systematic Reviews and Meta-Analyses)** に厳密に準拠したシステマティック・レビューを実施する。

### 3.1 データベースおよび検索戦略

情報の網羅性とHCI分野・心理・認知科学分野における権威性を担保するため、以下の主要学術データベースを対象とする。

- **ACM Digital Library**
- **IEEE Xplore**
- **PubMed**
- **Scopus**
- **PsycInfo** (PubMedでの検索が不十分な場合の補完として導入)

検索クエリは、「没入環境」「身体表象」「知覚評価」の3つのコンセプトをAND条件で結合し、TitleおよびAbstractを対象に実行する。

> **Unified Search Query（現行・Rev.6, 2026-07-17 著者確定。再検索は実施待ち）:**
`("Virtual Reality" OR "VR" OR "HMD" OR "head-mounted display" OR "head mounted display"
 OR "Virtual Environment*" OR "immersive virtual") AND
("Avatar" OR "Body" OR "Embodiment") AND
("Size" OR "Scale" OR "Height" OR "Distance")`

> **G1 拡張の理由（Rev.6、スコープは不変）:**
> - "head-mounted display": VRの装置的定義であり心理学系文献の慣用表現。同義語追加でありスコープ拡大ではない
> - ハイフン無し表記の併記: DB間のトークン正規化差異への対応
> - "Virtual Environment*": 再現率優先。非HMD系（CAVE等）の混入は Phase 3b の人手スクリーニングで除外可能
> - "immersive" 単独は不採用: "immersive learning" 等の非VR文献を大量に拾い precision を損なうため "immersive virtual" に限定

> **履歴:** 初回検索（2025-12〜2026-05 実行）で使われたのは G1 = ("Virtual Reality" OR "VR" OR "HMD")
> の旧版である（Rev.5 で記録訂正）。G1 の狭さによる既知文献の取りこぼし（例: Being Barbie）が
> Known-Item Test で確認されたため Rev.6 で拡張した。旧版と Rev.6 の差分ヒットは再検索の第2波
> として PRISMA に報告する。

### 3.2 文献選定プロセス (Screening Process)

> **プロトコル改訂 (2026-07-16):** 本サーベイでは包含/除外判定に LLM を一切使用しない。理由: (a) モデルバージョン依存で第三者再現が不可能、(b) プロンプト感度の報告方法が確立していない、(c) PRISMA/Kitchenham 系ガイドラインに標準手続きが存在しない。全ての自動判定は決定論的基準に限定し、意味的判断は人手ダブルスクリーニング（Cohen's κ 報告）で行う。旧版の「AI支援による要旨判定」（HCI/心理の分岐フロー）は本改訂で廃止した。変更履歴は `protocol_changelog.md` を参照。

選定フローは全データベース共通の単一フローとする（旧版の HCI / 心理分野の分岐は AI 判定戦略の違いに由来したため、廃止に伴い統合）。

- **Phase 1: 重複削除（決定論的・実装済み）**
    - DOI 完全一致 → Zotero Key 完全一致 → 正規化タイトル完全一致の優先順位で検出し、先出レコードを正とする。
- **Phase 2: 学会ランクスクリーニング（決定論的・実装済み）**
    - **照合手順（Rev.6）:** ① 著者確認済み **Venue エイリアス表**（`venue_aliases.csv`）を最優先で参照
      → ② CORE 正規化完全一致 → ③ SJR ISSN/完全一致 → ④ ファジー照合（最後の手段）。
      エイリアス表は誤照合（例: Presence誌→同名ワークショップ、TAP誌→SAPシンポジウムの
      正規化同名衝突）の防止が目的であり、**照合漏れによる除外とランク基準による除外を
      PRISMA 上で区別して記録**する（除外理由コード `via author-verified alias`）。
    - **カンファレンス:** 学会ランク（CORE Ranking）**A* または A** のみ採用
    - **ジャーナル:** 分野別ランク（SJR 2025）**Q1（上位25%）のみ採用**（2026-07-17 確定, Rev.4）。
      Q2以下の除外により主題関連誌の一部（IEEE Trans. on Haptics, Cognitive Processing,
      Multisensory Research 等、計826件/332誌）が対象外となることは認識のうえでの決定であり、
      その影響は Threats to Validity 節で報告する（証拠: `outputs/sjr_q2_excluded_venues.csv`、
      Known-Item での実例: Gulliver's virtual travels = Cognitive Processing Q2 脱落）。
- **Phase 3a: 決定論的キーワード除外（実装済み・`pipeline.py`）**
    - Title + Abstract に対する正規表現マッチング（大文字小文字区別なし・単語境界 `\b` 適用）。マッチした文献を除外する。全パターンと追加理由は下表の通り（適格性基準 PICOS との対応を明記）。

    | カテゴリ | 除外パターン | 追加理由（適格性基準との対応） |
    | --- | --- | --- |
    | Cat1 非没入・スコープ外 | `desktop display` `desktop monitor` `computer monitor` `flat-screen` `flat panel` `2d display` | 非没入型ディスプレイ研究の除外（I基準: HMDを用いたVR環境が介入の前提） |
    | Cat1 | `augmented reality` `ar` `mixed reality` `mr` | AR/MRでは実環境が視野に残り、完全な視覚的置換を前提とする自己スケール操作が成立しないため（I基準） |
    | Cat1 | `360[-]video` `spherical video` `panoramic video` `omnidirectional video` | 実写全天球映像の受動視聴は身体表象の操作を伴わないため（I基準） |
    | Cat1 | `smartphone` `mobile phone` `tablet` | モバイル画面提示＝非没入のため（I基準） |
    | Cat1 | `projection mapping` `projected display` `cave automatic virtual` `cave system` `cave display` | HMD以外の投影型提示（自己身体が実視野に残る）のため（I基準） |
    | Cat2 技術論文・非実証 | `rendering algorithm/engine/pipeline/technique/performance` `real-time rendering` `shader` `gpu` | 描画技術の提案・性能評価でありユーザー実験を伴わないため（S基準: 実証研究） |
    | Cat2 | `point cloud` `depth camera` `stereo reconstruction` | 3D再構成・センシング技術の提案のため（S基準） |
    | Cat2 | `motion-to-photon` `frame rate` `refresh rate` `tracking algorithm` `segmentation algorithm` `optimization algorithm` | 表示遅延・アルゴリズム性能の評価であり知覚実験でないため（S基準） |
    | Cat2 | `technical report` `system architecture` `software framework/architecture/library` | 非実証的な技術文書のため（S基準） |
    | Cat3 臨床・医療 | `rehabilitation` `physical therapy` `occupational therapy` | リハビリテーション研究の除外（P基準: 健常成人） |
    | Cat3 | `cognitive behavio(u)ral therapy` `exposure therapy` `therapeutic intervention` | 治療目的の介入研究のため（P/I基準） |
    | Cat3 | `surgical training/simulation/procedure/planning` `surgery` `laparoscop*` `minimally invasive` | 外科手技・手術支援研究のため（スコープ外） |
    | Cat3 | `patient(s)` `clinical trial/study/outcome/setting/population` `stroke ...` | 患者対象・臨床研究のため（P基準・S基準） |
    | Cat3 | `phobia` `ptsd` `post-traumatic stress` `autism spectrum` `dementia` `alzheimer` `psychosis` `schizophrenia` `neurological disorder...` `psychiatric ...` | 特定疾患集団を対象とするため（P基準: 健常成人） |
    | Cat3 | `chronic pain` `pain management` `pain relief` | 疼痛治療への応用研究のため（スコープ外） |

    - 正確な正規表現の全文は `pipeline.py`（EXCLUSION_CATEGORIES）を正とし、パターン別ヒット件数は `pipeline_log.txt` に記録される。パターンを追加・削除した場合は本表・`protocol_changelog.md`・README を同時に更新する。
- **Phase 3b: Title/Abstract 二重スクリーニング（人手）**
    - Phase 3a 通過文献の全件に対し、**評価者2名が独立に** Title/Abstract を読み、適格性基準（§Phase 4 の PICOS を Title/Abstract レベルに緩和したもの）で Include / Exclude / Unsure を判定する。
    - 評価者間一致度として **Cohen's κ を算出・報告**する。判定の不一致および Unsure は2名の**協議（consensus meeting）**で解決し、解決できない場合は Include 側に倒して Phase 4（全文評価）へ送る（再現率優先）。
    - 判定シート（文献ID・両評価者の判定・最終判定・協議メモ）を成果物として保存し、監査可能性を担保する。

### Phase 4: 全文適格性評価 (Full-Text Eligibility)

最終候補の全文を精査し、以下の**PICOS基準**を満たす実証研究を最終的な分析対象として採択

- **P (対象者):** 健常成人（小児、高齢者、疾患患者は除外）
- **I (介入):** HMDを用いたVR環境下での身体・空間スケール操作、および多感覚刺激の提示
- **C (比較対象):** スケール操作の有無、異なる倍率間の比較、または視覚単独vs多感覚刺激の比較
- **O (評価指標):** 自己・環境のスケール変容を測る定量的データ（主観的サイズ推定、距離知覚、アフォーダンス判断、身体所有感、客観的運動出力）
- **S (研究デザイン):** 客観的なユーザー実験に基づく実証研究

### 3.3 分類体系

採択された文献を構造化するため、多層的なTaxonomyを定義

### (1) 介入モダリティの階層化 (Stimulus Modality)

- **Unimodal:** 視覚情報のみを操作する古典的アプローチ（Visual-Global / Local / Perspective）
- **Multimodal (two-way):** 視覚を含む2つの感覚情報の同期（Visual-Tactile / Motor / Auditory）
- **Multimodal (three-way or more):** 視覚を含む3つ以上の感覚情報の同期・操作による高度な身体化アプローチ（例: Visual-Tactile-Auditory）

### (2) 評価指標の志向性

- **Self-scale Dominant (S):** 自己の身体サイズの変容を測定。
- **World-scale Dominant (W):** 外界の環境、物体、距離の変容を測定。
- **Ambiguous/Mixed (A):** 自己と世界の尺度が未分離・混在している。

### (3) 認知プロセスの基盤（パワーバランスの決着）

知覚形成の背後にある「ベイズ的な重み付け（最尤推定）」に着目し、現在の感覚刺激（Stimulus/Likelihood）と、過去の記憶・文脈（Context/Prior）のどちらが最終的に知覚を支配したかという「結果の着地点」で分類する。

| 分類項目 | 定義（その研究はどう結論づけたか？） | 意義 |
| --- | --- | --- |
| **Stimulus-Overriding
(**感覚入力が文脈を上書きした) | 足音や振動、強い視覚同期などの**物理的刺激**が、環境の事前知識を打ち破り、身体図式の更新（自己サイズの変容）に成功したと報告する研究。 | 「どのような刺激を与えれば、文脈の呪縛を解けるのか」を明らかにする。 |
| **Context-Dominant
(**文脈が感覚入力を抑え込んだ) | 刺激を与えたが、「ビルが縮むはずがない」等の**トップダウンの事前知識**や文脈手がかりが勝り、ミニチュア効果などの環境変容・エラーが生じたと報告する研究。 | 「視覚単独や不十分な刺激では、なぜ脳が自己拡大を拒否するのか（限界）」を証明する。 |
| **Conflict / Threshold
(**両者の拮抗・閾値を探った) | 刺激と文脈を意図的に衝突させ、「どの倍率・どの条件下で知覚が反転するか」の境界線（パワーバランスの逆転ポイント）を調査した研究。 | 本研究（実験）の「〇倍まではStimulusが勝つが、それ以上はContextが勝つ」という議論に直結する。 |

*(※理論的背景: なぜ多感覚（Multimodal）がStimulus-Overridingに寄与しやすいのかについては、情報の信頼性に基づく最尤推定（MLE）モデルをレンズとして考察で論じる)*

---

## 4. 期待される知見と貢献 (わかったらいいなぁ)

本分類データを用いた分析を通じて、以下の点が明らかになれば、貢献になりそう.

- 年代ごとのTaxonomy・分野の変遷
    - 何年ごろから多感覚刺激を用いる研究が頻繁にされるようになったのか？
    - HMDの普及・今普及しているHMDの発表年度との関係は？
    - 心理学と関連の深い研究はいつごろから？何きっかけ？
    - カテゴリーは年々増えてる？それとも減ってる？
    →もし減ってないとしたら、いまだに視覚のみで研究が続けられているのはなぜ？
- Venueごとの流行り
    - どこの学会・論文誌でよく扱われている？通りやすい？
    - 多感覚を扱いだすのが早かったところは？
    → その学会・論文誌の特徴と結びつけて、こういう傾向があるかも？を検討
- タスクの有効性検討:
    - 研究で用いられているタスク（把持、歩行、距離推定など）と、有効だった感覚モダリティのクロス集計してみる
    - 「静的な距離推定には視覚が強いが、動的なインタラクション（歩行など）には行動随伴的な聴覚・触覚が必須である」といった傾向を見つける
- 自己スケールを操作するための非視覚的パラメータを体系化する。
    - *聴覚なら「ピッチ（重さの表現）」「残響（高さ・空間の表現）」「遅延（スケールの表現）」*
    - *触覚なら「周波数」「振幅」など*
- ソーシャルVR・メタバース設計への示唆
    - VRChatなどの実社会への応用を見据え、「他者アバタが存在する環境（Social Context）」と「単独環境（Solo Context）」でスケール感覚の研究がどう分かれているか, 未開拓なのはどちらかを指摘？
- ユーザー多様性と個人差
    - 既存研究の被験者の「現実の身長」「VR経験値」「性別」などが結果にどう影響しているかを分析する。（例：「高身長の人と低身長の人で、巨大化アバタへの順応速度は違うのか？」といった個人差を考慮した研究はある？