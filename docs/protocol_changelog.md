# Protocol Changelog — プロトコル変更履歴

> システマティック・レビューのプロトコル(`rule.md`)に対する全変更を日付つきで記録する。
> ACM Computing Surveys の方法論セクション(protocol deviations の報告)に転用するため、
> 各項目は「変更内容 / 変更理由 / 影響範囲」を明記する。

---

## 2026-08-11 — Rev.11: gold set の見直しと記録の整合化(全文書監査の結果)

全文書を突き合わせた監査で見つかった齟齬について、著者が4点を確定した。

### (1) gold set #3 Kilteni 2012 を in-scope → **background** に変更

**理由:** #3 は `InterventionModality = N/A` / `TheoreticalBasis = Theory` の**用語定義論文**であり、
同じセクション「I. 理論的前提」の他の4件(#1 Gallagher / #2 Tsakiris / #19 Botvinick&Cohen /
#20 Lenggenhager)はいずれも background である。#3 だけが in-scope だった。
PICOS 上、#3 は I(HMD下でのスケール操作)にも S(客観的ユーザー実験)にも該当せず、
**Phase 4 でどのみち除外される**。除外される論文を recall の分母に置くと、
「プロトコルが除外する論文を検索が拾えなかった」ことを減点することになる。

**影響(数値の更新):**

| 指標 | 旧(分母13) | 新(分母12) |
|---|---|---|
| step0 recall | 69.23% (9/13) | **66.67% (8/12)** |
| step2 recall | 23.08% (3/13) | **25.00% (3/12)** |
| venue フィルタで脱落した known-item | 6件 | **5件**(#7/#8/#13 unmatched, #10 below_rank, #14 criterion) |

### (2) **Rev.10 の根拠数値を訂正** — TA 確定に recall コストは無かった

Rev.10 で「TA 準拠だと step0 recall が 69.2% → **61.5%** に落ちる」「`ResearchVR4.csv` は
scope 非均質なので第三者は 61.5% しか再現できない」と記載したが、**この 61.5% は #3 を
分母に含めた場合の値**であった。#3 を background に移した現在、再計算すると:

| 対象 | レコード数 | step0 recall |
|---|---|---|
| 全体(第1波+第2波) | 26,434 | 8/12 = **66.7%** |
| 第2波のみ(TA準拠) | 12,533 | 8/12 = **66.7%** |
| 第1波のみ(scope混在) | 13,901 | 8/12 = **66.7%** |

**三者は同値であり、第1波にしか無い gold は存在しない。**
scope の非均質性が known-item recall に与える影響は**ゼロ**であった。
これは TA 確定の判断を弱めるものではなく、**むしろ強める**(TA にすることの recall 上の
コストが実測でゼロだった)。Rev.10 の結論は維持し、根拠の記述のみ差し替える。

> **Threats to Validity での扱い(変更あり):** 「TA で再現した第三者の recall は 61.5%」という
> 記述は**撤回**する。ただし第1波IEEEの1,077件が第2波に現れない(TAで3群成立は4.7%)という
> **コーパスの scope 非均質性そのものは事実として残る**ため、その記載は維持する。
> 非均質なのはコーパスであって、known-item recall には表れなかった、というのが正確な記述である。

### (3) IEEE 第2波のヒット数は **361件** で確定

旧記録の 379件(2026-08-01 の UI 表示値)は**誤りとして扱う**。当該値は ACM の「81件」が
構文エラーと判明したのと同じセッションで記録されたものであり、信頼性が低い。
`search_strings.md` では 361 を正とし、379 は経緯として注記に降格する。

### (4) Scopus 第1波のフィールド指定は **TITLE-ABS-KEY** と記録する

`search_strings.md` の表セルは「Title, Abstract」、注記は「実際は TITLE-ABS-KEY だった
可能性が高い」で矛盾していた。件数の整合(第1波 4,331件は TITLE-ABS 2,533件より多く、
TITLE-ABS-KEY 4,727件と整合する)にもとづき **TITLE-ABS-KEY で実行された**と確定し、
**第1波と第2波で scope が異なる**ことを PRISMA-S に明示する。

### (5) ACM 第2波の「和集合方式」を逸脱として正式に記録(記録漏れの解消)

ACM 第2波は `Title:` 検索と `Abstract:` 検索を**別々に実行してその和集合**を取っている
(6,013 + 8,331 → ユニーク 9,630)。群ごとに `(Title:G OR Abstract:G)` を入れ子にした
単一クエリではないため、**フィールド横断の一致**(例: G1 はタイトルのみ、G2 は要旨のみに出現)を
取りこぼす。gold set 12件中11件が Abstract のヒットに依存しており、机上の懸念ではない。
**PRISMA-S および Threats to Validity に逸脱として明記すること。**
(本項は Rev.9 時点で「Rev.10候補」として残タスク化されていたが記録されていなかった。)

### 影響範囲

**【2026-08-12 追記】gold set #6 のタイトル誤記を修正。** `known_item_test.py` に偽陽性検出を
実装したところ、#6 Banakou et al. 2013 のタイトルが実物と食い違っていたことが判明した
(旧 `...and implicit self-identification with child-like attributes` →
新 `...and implicit attitude changes`)。DOI は正しかったため **recall には影響しない**(8/12 のまま)。
2026-08-03 の監査で「他の項目にも同種の誤りが残っている可能性」と記録されていたものの実例であり、
機械的な検出手段ができたことで再発を防げるようになった。

- `self_scale_references.csv`(#3 の SearchScope、#6 の Title)、`outputs/venue_dropped_known_items.csv`(6→5件)、
  `outputs/known_item_test.csv`、`known_item_analysis.md` を再生成済み
- `scripts/snowball_search.py`: #3 は background になり既定シード(in-scope由来)から外れるため、
  **後方探索専用シードとして明示的に追加**する処理を `load_default_seeds()` に追加した。
  #3 の後方探索は心理接合点の古典4件すべてに到達しており、`snowballing_protocol.md` §1(3) の
  「background 到達目標」の点検を担っているため、失ってはならない
- gold set の in-scope は **12件**。目標15〜25件に対し依然として下限割れであり、拡充は継続課題

---

## 2026-08-10 — Rev.10: 検索scope を TA に確定 / スノーボーリング手続きの分離と効率化

### 変更内容 (1): 実効 scope を **Title-Abstract (TA)** に最終確定

Rev.7 以来「TA 基準、Scopus の Keyword が再取得できれば TA+K へ格上げ可」として
保留していた scope 判断を、**TA 維持で確定**する。TITLE-ABS-KEY への移行は行わない。

### 変更理由

第2波(ACM 9,630 / IEEE 361 / Scopus 2,542)を統合した `ResearchVR4.csv`(26,434件)で
Known-Item Test を実測した結果にもとづく:

| 対象 | レコード数 | step0 recall |
|---|---|---|
| 全体(第1波+第2波) | 26,434 | 9/13 = 69.2% |
| 第2波のみ(TA準拠) | 12,533 | 8/13 = 61.5% |
| 第1波のみ(scope混在) | 13,901 | 9/13 = 69.2% |

- **第2波の 12,533件は gold set を1件も新規回収しなかった**(Rev.6 の G1 拡張は
  Being Barbie の回収を狙ったものだったが、効果なし)。
- 第1波にしか存在しない gold は **#3 Kilteni 2012 の1件のみ**。同論文は
  **タイトルにも要旨(1,135字)にも G3語(size/scale/height/distance)が1つも無く**、
  TA では構造的に到達不能。第1波で捕捉できていたのは、IEEE 第1波が記録に残っていない
  より広いフィールドscope(All Metadata 等)で実行されていたためである
  (第1波IEEE 1,573件のうち第2波に残らなかった 1,077件は、**TA で3群が成立するのは 4.7%** に
  すぎない。第2波に残った 322件は 91.0% が成立)。
- したがって TAK への移行が救えるのは #3 のみであり、しかも #3 のキーワードに G3語が
  あるかは未確認(IEEE エクスポートの `Manual Tags` は `notion` プレースホルダで判定不能)。
- 一方、TAK は Scopus 実測で 2,533 → 4,727件(+87%)。Phase 3b は人手2名/件の手続きであり、
  **確実でない1件の回収のために人手工数をほぼ倍増させる判断は割に合わない**。
- 残る本物の脱落4件のうち **Wolf et al. 2020 はタイトルだけで3群すべて成立**しており、
  フィールドscope の問題ではない(当該論文の索引の問題)。TAK では直らない。

**代替の回収経路:** #3 を含む脱落文献は **Phase 2 の後にスノーボーリングで回収**する
(`snowballing_protocol.md` §0/§1.1)。scope を広げて全件を機械的に増やすのではなく、
既知の脱落を名指しで回収する方が、工数あたりの回収効率が高い。

### 影響範囲

- `search_strings.md`: TA 確定。「TA+K へ格上げ可」の留保を削除する(**要反映**)
- **Threats to Validity に必ず記載**:
  (a) TA は旧第1波の実効scope(TAK 相当)より狭く、Scopus で -46%、IEEE で -77% であること
  (b) 索引語経由でのみ到達可能な文献の残余リスクはスノーボーリングで緩和する設計であること
  (c) **`ResearchVR4.csv` は第1波(scope混在)と第2波(TA)の和集合であり、scope が均質でない**。
      プロトコルどおり TA で再現した第三者の step0 recall は 69.2% ではなく **61.5%** になる
- Known-Item Test の報告値は、上記の非均質性を明記したうえで両方を併記する

---

## 2026-08-10 — Rev.10 (2): スノーボーリングの目的分離と工数の圧縮

### 変更内容

`snowballing_protocol.md` を改訂し、以下を分離・追加した。

1. **(A) 既知文献の回収と (B) 未知文献の発見を分離**(§0)。
   step2 脱落の Known-Item 6件は **DOI で直接回収**し、citation searching は使わない。
   6件は探索の**シード**であって回収**対象**ではない。
2. **シードの性質による扱いの差**(§1.2)。1ホップ実測(1,854行/新規1,433件)で、
   主題シード5件(#7/#8/#10/#13/#14)は計185件・G3語密度 18〜59% であるのに対し、
   **#3(用語定義論文)だけで新規の 87%(1,248件)を占め、G3語密度は 0.9%** と2桁低い。
   #3 は被引用1,500件超の定義典拠であり、前方探索が身体化研究全体を引いてくるため。
3. **`found_abstract` と概念群スコア `kw_g1/g2/g3/kw_groups` を出力に追加**(§4.5/§4.6)。
   従来のログは要旨を持たず、**Title/Abstract を読む Phase 3b にそのまま使えなかった**。
   また新規1,433件のうち**タイトルのみで3群が揃うのは0件**で、トリアージも成立しなかった。

### 変更理由

「6件を回収するために1,433件を人手で読む」設計になっており、手段と目的が逆立ちしていた。
上記により人手判定の対象は **1,433件 → 約200〜400件** に圧縮される。

### 影響範囲

- `scripts/snowball_search.py`: `REF_CIT_FIELDS` に `abstract` を追加、`kw_flags()` を新設、
  出力を12列→17列に変更。旧ログへの追記は**列構成の照合で中断**する(黙って壊さないため)
- **旧 `outputs/snowballing_log.csv`(12列)は退避が必要** →
  `outputs/snowballing_log_pre20260810.csv`
- `kw_groups` は**読む順序専用**。足切りに使う場合は適用範囲・閾値・除外件数を
  PRISMA-S に逸脱として明記する(§4.6)

### 追記(2026-08-11 著者確定): #3 は後方探索のみとする

**#3 を前方探索のシードから外し、後方探索は残す**ことを確定した(`snowballing_protocol.md` §1.3)。

判断材料として #3 由来の前方・新規1,188件を目視した結果、G3語を含む11件のうち
**実際に主題適合なのは2件のみ**であった(残り9件は `embodiment scale`=質問紙尺度、
`Large-scale`=システム規模、`aesthetic distance`=比喩、`heightism`=身長の社会学 等の誤爆)。
一方 **#3 の後方探索65件は、本プロトコルが「到達目標」としていた心理接合点の古典
(Botvinick&Cohen 1998 / Lenggenhager 2007 / Slater 2010 / Petkova&Ehrsson 2008)に
すべて到達**しており、PsycINFO 不使用の残余リスク点検という役割を果たしている。

あわせて **後方探索のメタデータ補完を必須化**した(§1.4)。Crossref フォールバック経由の
参考文献は DOI しか返らない項目が多く、実測で後方173件中 **93件(54%)がタイトル欠落・
要旨は全件欠落**だった。この状態では Title/Abstract を読む Phase 3b にかけられないため、
DOI を持つレコードは S2 の `/paper/DOI:` で解決してから記録する。

**PRISMA-S への記載(必須):** 「シード1件(定義典拠論文)については前方探索を実施していない。
理由は被引用が主題非依存であり、実測で新規1,188件中の主題適合が2件であったため」。

**影響:** 人手判定の対象は **1,433件 → 約245件**(主題シード5件の185件 + #3 後方60件程度)。
実装は `scripts/snowball_search.py` の `DEFINITIONAL_SEEDS` と `--no-forward-seeds`、
および `resolve_missing_metadata()`。

---

## 2026-08-01 — Rev.9: 評価者体制を3名・ペア分担に確定(Phase 3b / Phase 4)

### 変更内容

**Phase 3b(Title/Abstract 二重スクリーニング)および Phase 4(全文適格性評価)の評価者を3名に確定した。**

| 役割 | 氏名 |
|---|---|
| 評価者 | 著者 |
| 評価者 | Yuta Kataoka |
| 評価者 | Ryoichi WATANABE |

**方式: ペア分担による二重スクリーニング。** 文献集合を3ブロックに分け、各ブロックを
異なる評価者ペア(著者×Kataoka / 著者×WATANABE / Kataoka×WATANABE)に割り当てる。
各文献は必ず2名が独立に評価する。

**一致度統計: ペアごとの Cohen's κ を算出し、その平均を報告する。**
3名全員が全件を評価する設計ではないため Fleiss' κ は用いない。
κ はペア別の値と平均の双方を報告し、ブロック間の判定傾向の偏りを点検する。

**却下した代替案: Fleiss' κ(全件×3名)。** 報告は最も素直だが工数が1.5倍
(Phase 3a 通過 1,827件の場合、全件×3名=5,481判定 に対しペア分担は 3,654判定)になり、
得られる精度向上に見合わないと判断した。

**不一致の解決:** 担当ペアの協議で解決し、決着しない場合は3人目を加えて多数決。
Phase 3b で解決できないものは Include 側に倒して Phase 4 へ送る(再現率優先、従来どおり)。

**必須の記録:** 判定シートに**担当ペア列**を持たせる(κ の算出単位になるため)。
Phase 4 では除外理由(PICOS のどの基準に抵触したか)を1件ずつ記録する。

### 変更理由

全文精査は Title/Abstract 段階より判断コストが高く、PICOS の境界事例(特に
「健常成人」「比較条件あり」「定量指標」の3要件)で判断が割れやすい。評価者を増やすことで
一致度の推定を安定させ、PRISMA 2020 Item #6(選定プロセスに関与した評価者数と独立性の報告)への
記述を強化する。

### 影響範囲

1. **`rule.md` 本文に反映済み**(2026-08-01): Phase 3b の「評価者2名・Cohen's κ」を
   3名ペア分担・ペアワイズκ平均に書き換え、Phase 4 に「評価体制」節を新設。
2. **工数の見積**: Phase 3a 通過 1,827件(現行値)の場合、Phase 3b は 3,654判定 ÷ 3名 = **約1,218件/人**。
   従来の2名全件方式(1,827件/人)より軽い。件数は第2波再検索後の公式再実行で変動する。
3. **判定シートの様式変更**: 担当ペア列の追加が必須。Phase 4 では除外理由(PICOS のどの基準か)の
   1件ごとの記録も必須。
4. **キーワードスコアの位置づけを明確化**: `simulate_screening.py` のスコア(0〜3点)は
   Phase 3b の**読む順序のトリアージにのみ使用可**とし、**スコアによる自動除外は行わない**と rule.md に明記。
   低スコアが内容起因か Abstract 欠損起因かを区別できないため(2026-05-25 のタスク1B 試算で
   Cat3 ヒット率 3.4%・Abstract欠損 30.8%)。これは新規の制限ではなく、
   従来どおり「未採用」であった運用の明文化。
5. **未反映**: Rev.8 の内容(3DB構成・scope=TA・Threats への PsycINFO 正当化と Venue 取りこぼし)は
   引き続き `rule.md` 本文に未反映。第2波再検索の完了後にまとめて反映する。

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
