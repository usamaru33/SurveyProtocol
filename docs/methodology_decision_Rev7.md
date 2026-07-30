# Methodology Decision — Rev.7(検索方法論のデータ検証と最終確定)

> 2026-07-21。5つの暫定方針をゼロ設計し直すのではなく、**現状の成果物・raw データで
> 数値検証し「支持 / 修正」を判定**する。数値の裏付けがない方針変更はしない。
> データが不足する項目は「判断保留・要データ」と明記する(勝手に仮定で埋めない)。
>
> 検証はすべて決定論的(DOI/正規化タイトル一致、列充足カウント)。LLM/API 不使用。
> 一次証拠: `outputs/known_item_test.csv`、`raw/{acm,ieee,PubMed,Scopus}.csv`、
> `outputs/raw_db_audit.csv`。既存 step ファイルは未変更(分析のみ)。

---

## エグゼクティブ・サマリ(先に結論)

| # | 暫定方針 | 判定 | 根拠となる数値(要約) |
|---|---|---|---|
| 1 | 4DB維持 | **支持(条件付き)** | Scopus は known-item #10 の唯一の情報源+#5/#6/#14 を ACM/IEEE の代わりに捕捉(corpus-unique 3,247件/75.4%)。**PubMed は known-item 限界寄与=0**(全 PubMed known-item は Scopus にも在る)だが corpus-unique 175件+心理系唯一の専門DB。→ 4DB維持。ただし **PubMed の正当化は known-item では示せていない**ことを明記 |
| 2 | 実効scope を TAK に統一 | **修正** | 列充足が非対称: **ACM の Abstract は 4.3%(342/7,997)しか無い**。**usable な Keyword 列は PubMed のみ**(MeSH 95%)。ACM の Manual Tags は item-type ("conference" 等)の混入で、Scopus は 1.2%。→ **一律 TAK は現エクスポートでは不可能**。共通分母は Title(全DB 100%)、Abstract は ACM で欠落。K は PubMed のみ |
| 3 | フィルタ層で正規化クエリ再適用 | **支持(要 degrade 設計)** | 4DB は Zotero 完全同一スキーマ(列の枠組みは揃う)→ 再適用の**実装は可能**。ただし列の**中身**が非対称(方針2)なので、レコード単位で「利用可能フィールドのみ」に落とす degrade 処理と PRISMA-S 明記が必須 |
| 4 | PubMed のみ MeSH 活用 | **修正(格下げ・要データ)** | MeSH は Manual Tags に格納済み(95%)で post-hoc 利用可能。しかし **known-item での MeSH 恩恵=0**(step0 欠落4件のうち3件は Frontiers VR=PubMed 非収載でMeSH適用外、1件 Being Barbie は PubMed raw に不在)。→ 検索を分岐させる根拠は無い。MeSH は「フィルタ層内の追加recallブースタ+PRISMA-S 報告項目」に格下げ。**corpus全体の便益はライブ差分テストが必要=判断保留** |
| 5 | Known-Item Test(step0≥80%) | **支持(未達・セット要拡充)** | 方法論として支持。現 step0 = **9/13 = 69.2%** で目標未達。セットは 13件(最低ライン)、心理接合点 seminal(Botvinick&Cohen 1998 / Lenggenhager 2007)未収録。→ Rev.6 再検索後の再測定+セット拡充が条件 |

**最重要の副次発見(5方針の外だが数値上の支配要因):**
Known-item の脱落の**主因は検索段階でも DB 構成でもなく、Venue ホワイトリスト(CORE A\*/A + SJR Q1)**である。
13件中 **6件が step2 で脱落**(#3, #7, #8, #10, #13, #14)。検索式・scope・DB の議論より、
venue フィルタの学際会場取りこぼしの方が recall への影響が大きい。§Zhou対比・Threats で扱う。

---

## A. Known-Item セットの掲載誌内訳(心理接合点の主張は根拠を持つか)

### A-1. in-scope 13件の venue 分類

一次データ: `self_scale_references.csv`(SearchScope=in-scope の 13件)。

| 分類 | 件数 | 該当(# = self_scale_references.csv の ID) |
|---|---|---|
| VR/CG/HCI 会場 | **9 (69%)** | #3 Presence, #7 Augmented Human, #8 ACM SAP, #9/#12/#18 Frontiers in Virtual Reality, #10 ICAT-EGVE, #11 IEEE VR, #13 ACM TAP |
| 心理・神経科学系ジャーナル | **4 (31%)** | #4 PLoS ONE(Being Barbie/Ehrsson), #5 PLoS ONE(Welcome to Wonderland), #6 PNAS(Banakou/Slater), #14 Cognitive Processing |

背景文献(SearchScope=background、検索対象外として意図的に除外、心理寄り):
#1 書籍(Gallagher), #2 Experimental Brain Research(Tsakiris), #15 ACM CHI(Tajadura-Jiménez, 聴覚),
#16 Frontiers in Psychology, #17 PLoS ONE(audio-tactile)。

### A-2. 心理接合点の中核 seminal 文献の点検 → **欠落あり(著者が追加すべき)**

サーベイが「心理学との接合点」を主張する以上、その接合を定義する古典が gold set にあるべき。
raw 4DB での実在も確認した(DOI 完全一致):

| seminal 文献 | known-item セット | raw 4DB 実在 | 扱い |
|---|---|---|---|
| Botvinick & Cohen 1998(Rubber Hand Illusion, Nature) | **無し** | **無し** | 著者追加を推奨(background) |
| Lenggenhager et al. 2007(Video ergo sum, Science) | **無し** | **無し** | 著者追加を推奨(background) |
| Slater et al. 2010(First-person body transfer, PLoS ONE) | 無し | 無し | 著者追加を検討 |
| Petkova & Ehrsson 2008(body swap, PLoS ONE) | 無し | 無し | 著者追加を検討 |
| Kilteni et al. 2012(Sense of Embodiment) | **有り(#3)** | 有り(IEEE) | 済 |
| van der Hoort/Ehrsson 2011(Being Barbie) | **有り(#4)** | **無し**(§C 参照) | 済(ただし step0 脱落) |

**判定:** 心理接合点を支える古典 RHI / 全身錯覚(Botvinick&Cohen 1998, Lenggenhager 2007)が
known-item セットに**含まれていない**。これらは非VR/前VR文献で実行クエリでは構造的に取れず
(background 扱いが妥当)、raw にも不在。**recall の分母には入れず、「接合点の境界を示す
background known-item」として著者が明示追加すべき**。これにより「どこまでが検索対象で、
どこからがスノーボーリング/手動追加か」の境界が PRISMA 上で明確になる。

---

## B. Scopus/PubMed の限界寄与(4DB維持の正当化の直接証拠)

### B-1. Known-Item レベル(`known_item_test.csv` の step0_source_dbs)

step0 を生存した 9件のDB出現内訳:

| # | Title(短縮) | 出現DB | 含意 |
|---|---|---|---|
| 3 | The Sense of Embodiment in VR | ieee のみ | IEEE 固有 |
| 5 | Welcome to Wonderland | PubMed; Scopus | **ACM/IEEEに無い** |
| 6 | Illusory ownership of a virtual child body | PubMed; Scopus | **ACM/IEEEに無い** |
| 7 | Distortion in Perceived Size | acm; Scopus | — |
| 8 | Influence of eye height and avatars | acm; Scopus | — |
| 10 | Dwarf or Giant | **Scopus のみ** | **Scopus 単独=唯一の情報源** |
| 11 | Object Size Perception in IVR | ieee; Scopus | — |
| 13 | Does Scaling Player Size Skew… | acm; Scopus | — |
| 14 | Gulliver's virtual travels | PubMed; Scopus | **ACM/IEEEに無い** |

**Scopus 無しで step0 消失する known-item: #5, #6, #10, #14 の 4件**
(内訳: 心理系 3件 #5/#6/#14 + CG系ワークショップ 1件 #10)。うち **#10 は Scopus が唯一の情報源**。
→ **Scopus の必須性は強く支持される**(load-bearing)。

**PubMed 単独 known-item: 0件**。PubMed が持つ known-item(#5, #6, #14)は**すべて Scopus にも在る**。
→ **known-item のレベルでは PubMed の限界寄与は 0**(Scopus が上位互換)。

### B-2. Corpus レベル(raw 4DB、DOI/正規化タイトルでの固有性推定)

| DB | 総(dedup) | 他3DBに無い固有 | 固有率 |
|---|---|---|---|
| ACM | ~7,447 | ~7,305 | 98.1% |
| IEEE | 1,276 | 924 | 72.4% |
| Scopus | ~4,308 | 3,247 | 75.4% |
| **PubMed** | 781 | **175** | **22.4%** |

ペア重複: PubMed∩Scopus **606** / IEEE∩Scopus 352 / ACM∩Scopus 142 / IEEE∩PubMed 39 /
ACM∩IEEE 0 / ACM∩PubMed 0。

**判定(方針1):**
- **Scopus = 維持を強く支持**(known-item #10 の唯一源、心理系 #5/#6/#14 を担う、corpus固有 3,247件)。
- **PubMed = 維持を支持するが根拠は弱い**。known-item 固有寄与=0。ただし
  (a) corpus固有 175件(=Scopus でも拾えない、22.4%)、
  (b) PsycInfo 未実行のため**心理系の唯一の専門DB**、
  (c) MeSH による心理系 recall の潜在価値(§C)。
  → 4DB維持だが、**「PubMed の正当化は現 known-item セットでは実証できていない」ことを本文に明記**し、
  心理系 known-item(§A-2 の追加分)で再検証すること。175件の主題適合率は未測定=要確認。

---

## C. TAK統一 vs PubMed-MeSH のトレードオフ(方針4の判断材料)

### C-1. MeSH は現データで利用可能か → **可能**

PubMed の `Manual Tags` 列に MeSH 見出し語が格納されている(**743/781 = 95%**)。
例: `Humans; Adult; …; *Amputees; *Phantom Limb/therapy; *Virtual Reality; *Virtual Reality Exposure Therapy; …`。
→ **フィルタ層で post-hoc に MeSH ベースの再判定を PubMed に対して行うことは技術的に可能**
(他DBには MeSH 列が無いので PubMed 固有処理)。

### C-2. MeSH は known-item の捕捉を改善するか → **現データでは改善 0**

step0 脱落 4件の内訳(raw 実在チェック済み):

| # | Title | 脱落原因 | MeSH で救えるか |
|---|---|---|---|
| 4 | Being Barbie(PLoS ONE 2011) | PubMed raw に**不在**(実行クエリで返らず) | ほぼ不可(PLoS ONE は MEDLINE 収載だが、MeSH「Virtual Reality」は2018導入で2011論文に付与見込み薄) |
| 9 | Effects of eye height…(Frontiers in VR 2020) | 誌が **PubMed/MEDLINE 非収載** | **不可(そもそも索引されない)** |
| 12 | Plausibility Paradox(Frontiers in VR 2021) | 同上 | **不可** |
| 18 | Enhancing Virtual Walking(Frontiers in VR 2021) | 同上 | **不可** |

**判定(方針4):MeSH を根拠に PubMed 検索を分岐させる便益は known-item では 0**。
既に in-scope の心理系 3件(#5/#6/#14)は実行 tiab クエリで捕捉済み。欠落 4件は MeSH で救えない
(3件は非収載誌、1件は用語年代のミスマッチ)。
→ **方針4 は「MeSH で検索を分岐/DB固有適応」から「フィルタ層内の任意の recall ブースタ+
PRISMA-S 明記項目」に格下げ**を推奨。これは方針2/3 と整合する(K scope は元々 PubMed でしか
populate されないため、MeSH 活用は「統一を壊す」のではなく「唯一の K 情報源を活かす」に相当)。
- **要データ(判断保留):** corpus 全体で MeSH 拡張検索が心理系 recall をどれだけ上げるかは、
  PubMed で `"Virtual Reality"[Mesh]` を OR したライブ差分検索を実行し、増分の主題適合を
  見るまで確定できない。現データからは判定不能。

---

## D. フィルタ層の実装可能性(方針3の検証)

一次データ: `raw/*.csv` の列充足カウント。4DB はすべて Zotero エクスポートで**列スキーマは完全同一**。

| フィールド | ACM (N=7,997) | IEEE (1,276) | PubMed (781) | Scopus (4,331) | 一律再適用の可否 |
|---|---|---|---|---|---|
| **Title** | 100% | 100% | 100% | 100% | ✅ 全DB可 |
| **Abstract Note** | **4.3%(342)** | 99.6% | 99.6% | 99.3% | ⚠️ **ACM 欠落** |
| **Keyword(usable)** | 0%※ | 一部のみ†| **95%(MeSH)** | **1.2%(51)** | ❌ PubMed 以外ほぼ不可 |
| Automatic Tags | 0% | 0% | 0% | 0% | ❌ 全DB空 |

- ※ ACM の `Manual Tags` は 100% 埋まっているが中身は item-type(`conference` 6,958 / `journal` 371 /
  `short` 325 / `workshop` 183)で、**著者キーワードではない**(キーワードとして使用不可)。
- † IEEE の `Manual Tags` は一部に実キーワード列を含むが、多くが `notion` プレースホルダ混入で信頼性低。

**判定(方針3):**
- **枠組みは実装可能** — スキーマが完全同一なので「取得後に同一の正規化クエリを再適用する
  フィルタ層」は Zhou et al. 2025 と同じ発想でコード化できる。
- **ただし「同一クエリを一律に」再適用はできない** — フィールドの**中身**が非対称。
  - Title: 全DBで再適用可(唯一の完全共通分母)。
  - Abstract: ACM では 96% 欠落 → ACM に対しては title-only へ degrade せざるを得ない。
  - Keyword: PubMed(MeSH)以外は使えない。
- **必須の設計対応:** フィルタ層は「レコードが持つ利用可能フィールドのみで判定し、
  degrade したレコードにフラグを立てる」方式にし、PRISMA-S に
  「ACM は Abstract 欠落のため title のみで正規化フィルタを適用した」旨を明記する。
- **再取得時に確保すべきもの(著者へ):**
  1. **ACM の Abstract**(現状 4.3%)— ACM DL から再エクスポート、または Crossref/S2 で補完。
     これが無い限り ACM に対する Title+Abstract 統一は成立しない。
  2. **Scopus の Author/Index Keywords**(現状 1.2%)— Scopus エクスポートで
     Keywords 列を明示的に含める。K scope を全DBで揃えたい場合の前提。
  3. 各DBの **verbatim フィールド指定構文**(TITLE-ABS-KEY か TITLE-ABS か / [tiab] の別)—
     `search_strings.md` で依然未記録。実効 scope の非対称の**源泉**を確定するのに必要。

---

## Zhou et al. 2025(arXiv:2507.18877)との対比

| 論点 | Zhou et al. | 本プロトコル(Rev.7) |
|---|---|---|
| **踏襲する点** | 取得後に正規化クエリをコードで再適用し、DB間の scope 差を吸収する Springer 処理 | 方針3 のフィルタ層として採用(スキーマ同一性 §D で実装可能性を確認) |
| 彼らの弱点①: **Known-Item 検証欠如** | recall を quasi-gold standard で検証していない | 方針5 で Known-Item Test を導入。**ただし現状 step0=69.2% で目標未達を自認**し、Rev.6 再検索後に再測定 |
| 彼らの弱点②: **学際会場の取りこぼしを Limitations で自認** | 検索段階での取りこぼしを認めるに留まる | 本プロトコルは Scopus/PubMed 必須化で**心理系 venue を実データで捕捉**(§A/B)。**ただし取りこぼしは消えたのではなく、検索段階から Venue フィルタ段階(step2)へ移動しただけ**(§下)。この自己認識を Threats に明記して補強する |

**補強の要点(彼らを超えるために正直に書くこと):**
本プロトコルの recall 最大の漏れは、DB でも検索 scope でもなく **Venue ホワイトリスト**である。
Known-item 13件中 6件(#3 Presence, #7 Augmented Human, #8 APGV/SAP, #10 ICAT-EGVE,
#13 MIG/ACM TAP, #14 Cognitive Processing)が step2 で脱落。うち #14 は SJR Q1 基準どおりの除外
(Rev.4)、残りは学際/ワークショップ会場の未収載・照合漏れ。
Zhou et al. が「検索段階の学際取りこぼし」を自認したのに対し、本プロトコルは
「**厳格な venue 品質フィルタが同じ学際取りこぼしを step2 で起こす**」ことを Known-Item Test で
定量化できている点が優位。この 6件をスノーボーリングで回収し PRISMA 右カラムで報告する運用
(方針5 の後段)で補強する。

---

## 著者に確認すべきこと(仮定で埋めていない項目)

1. **PubMed corpus固有 175件の主題適合率** — サンプル目視が必要。適合率が高ければ PubMed の
   独立した正当化になる。低ければ「PubMed は心理系 recall 保険+PsycInfo 代替」の位置づけに限定。
2. **MeSH 拡張のライブ差分** — PubMed で `"Virtual Reality"[Mesh]` OR を加えた再検索の増分。
   §C-2 の通り現データからは MeSH の corpus 便益を判定不能。
3. **ACM Abstract の再取得可否** — 現 4.3%。フィルタ層の Title+Abstract 統一の成立要件(§D)。
4. **Scopus Keywords の再エクスポート可否** — K scope を全DBで揃えるかの判断材料(§D)。
5. **心理接合点 background known-item の追加**(Botvinick&Cohen 1998 / Lenggenhager 2007 等、§A-2)—
   接合点主張の gold set 化。
6. **各DBの verbatim フィールド指定構文**(TITLE-ABS-KEY vs TITLE-ABS vs [tiab])— 実効 scope 非対称の源泉。
7. **known_items.md の位置づけ** — 現在テンプレート(有効行0)。実測は `self_scale_references.csv` を使用中。
   正式 gold set をどちらにするか(または 15〜25件へ拡充)を確定。

---

## Rev.7 確定事項と是正タスクの反映(2026-07-21 追記)

上記検証を受けて著者が確定した方針と、それに対応して整備した成果物:

**確定した方針(新規議論なし):**
- Scopus 維持(確定)。PubMed 維持(確定、ただし正当化は corpus固有 **175件の主題適合率**で裏付ける)。
- 実効 scope は**一律 TAK を放棄し Title-Abstract(TA)を基準**とする。Scopus の Keyword が
  再取得できれば TA+K へ格上げ可(その時点で Rev.8)。
- フィルタ層は「レコードが持つ**利用可能フィールドのみで判定 + degrade フラグ**」方式。
- MeSH は検索分岐の根拠にはせず、フィルタ層内の**任意 recall ブースタ + PRISMA-S 報告項目**に格下げ。
- Known-Item Test 維持、目標 step0 ≥ 80%。現 69.2% は Rev.6 再検索(第2波)後に再測定。

**Gold set の一本化(§著者確認#7 の解決):**
正式 quasi-gold standard は **`self_scale_references.csv`(SearchScope 列)に一本化**。
`known_items.md` の表は「拡充用の下書き」と位置づけ(冒頭に注記済み)。
Rev.7 で心理接合点の古典 2件を background として追加(#19 Botvinick & Cohen 1998、
#20 Lenggenhager 2007。非VR・実行クエリでは取れない前提、recall 分母外=検索対象と
スノーボーリングの境界を示す文献)。in-scope の 15〜25件への拡充は著者が
`self_scale_references.csv` に in-scope 行を追加して行う(現 in-scope 13件は最低ライン)。

**整備した成果物(このタスクで追加、外部通信・step ファイル変更なし):**
| 対象 | 成果物 | 実行 |
|---|---|---|
| ACM Abstract(4.3%)是正 | `search_replication.md` §Rev.7 是正 + `scripts/enrich_abstracts.py`(Crossref/S2 補完) | 著者(再エクスポート優先、API は fallback) |
| Scopus Keyword(1.2%)是正 | `search_replication.md` §Rev.7 是正(Author/Index Keywords を含む再エクスポート手順) | 著者 |
| verbatim フィールド構文の未記録 | `search_strings.md` §Rev.7 運用ルール(第2波で必須記録) | 著者(第2波時) |
| PubMed 固有 175件の適合率 | `scripts/pubmed_unique_audit.py` → `outputs/pubmed_unique_175.csv`(30件サンプルに judge 列) | 著者(目視判定・LLM不使用) |
| Venue 脱落6件の回収 | `scripts/venue_dropped_audit.py` → `outputs/venue_dropped_known_items.csv` + `snowballing_protocol.md` | 著者(スノーボーリング実施) |

`outputs/venue_dropped_known_items.csv` の分類実測: **unmatched 3件(#7/#8/#13)/ below_rank 2件
(#3 Presence, #10 ICAT-EGVE)/ criterion 1件(#14 Gulliver, SJR Q2 基準どおり)**。

## Rev.8 追記(2026-07-22): DB構成の最終確定と PsycINFO 正当化

著者確定。以後この方針で実装を進める(新規の方針議論はしない)。詳細版は
`protocol_changelog.md` Rev.8 を参照。ここでは PRISMA / Threats to Validity への
転用を見据え、**判断の根拠を一箇所にまとめる**。

### DB選定の最終構成

| DB | 採否 | 理由 |
|---|---|---|
| ACM Digital Library | 採用 | HCI・VR研究の中核会場 |
| IEEE Xplore | 採用 | HCI・VR研究の中核会場 |
| Scopus | 採用 | 学際的カバレッジ。心理系文献の実質的な捕捉源(下記) |
| **PubMed** | **不採用(Rev.8で確定)** | 医学・治療目的の文献が中心で本サーベイのスコープ外。
主題適合性が低いため選定基準を満たさない |
| PsycINFO | 不採用(既存の事実、Rev.5で確定済み) | アクセス制約により利用不可 |

**PubMed 不採用の位置づけについて(重要な区別):** Rev.7 の分析(§B: PubMed の known-item
固有寄与は0、corpus固有175件)は、**この決定の根拠として使っていない**。もし
「Scopus で代替できるから外す」という論法にすると、175件の主題適合率次第で決定が
揺らぎ得る脆弱な正当化になる。実際の決定理由は独立している:
PubMed は主題(医学・治療)が本サーベイのスコープと整合しないため、そもそも
選定基準(主題適合性)を満たさない。Rev.7 の分析結果は「参考情報」として本文脚注に
残すに留め、決定の主論拠には用いない(§下の「Rev.7分析の位置づけ」参照)。

### PsycINFO 不使用の正当化ドラフト(Threats to Validity 転用可)

> 本レビューは PsycINFO(APA PsycInfo)へのアクセス制約により、当該データベースでの
> 検索を実施していない。この欠落による心理学系文献の見落としリスクを、以下の根拠に
> より許容範囲と判断した。
>
> 第一に、Scopus は PsycINFO 収録誌の相当部分を索引しており、心理学分野の主要誌
> (PLoS ONE, PNAS, Cognitive Processing 等)は Scopus 経由で捕捉可能である。
> 第二に、この妥当性は事後的に quasi-gold standard(Known-Item Test, Kitchenham &
> Charters 2007)で実証されている: 本レビューが必須と判断した心理学系の代表文献
> 3件(#5 van der Hoort et al. 2013, PLoS ONE; #6 Banakou et al. 2013, PNAS;
> #14 Serino et al. 2020, Cognitive Processing)はいずれも Scopus によって捕捉され、
> このうち1件(#10 Kim & Interrante 2017, ICAT-EGVE)は **Scopus のみが捕捉した
> 唯一の情報源**であった(`outputs/known_item_test.csv` の `step0_source_dbs` 列、
> ACM・IEEE には不在)。第三に、Scopus 単独では捕捉しきれない残余の心理学系文献
> (特に PsycINFO 固有収録誌)については、引用探索(snowballing、`snowballing_protocol.md`)
> による前方・後方探索で補完し、PRISMA 2020 フロー図の "Identification via other
> methods" 側で透明に報告する。
>
> **限界の自認:** この設計は Scopus のカバレッジに強く依存しており、PsycINFO
> 固有(Scopus 非索引)の心理学系文献を体系的に見落とす可能性は残る。この残余
> リスクの定量評価(Scopus と PsycINFO の重複率など)は本レビューの範囲外であり、
> スノーボーリングによる部分的緩和に留まる。

### Rev.7 分析(PubMed 4DB前提)の位置づけ

本文書の §A〜D および上段の判定表は **Rev.7 時点(4DB前提)の分析**であり、
Rev.8 で3DB体制に確定した現在は**参考情報**として保存する(削除はしない)。
具体的には:

- §B「Scopus/PubMed の限界寄与」の数値(PubMed corpus固有175件、known-item固有寄与0)は、
  **PubMed不使用の決定理由ではない**(上記のとおり決定は独立)。ただし
  「Scopus が心理系 known-item を全て捕捉していた」という同じデータが、
  **PsycINFO正当化の実証根拠として転用**されている(§上記ドラフト参照)。
- §C(MeSH)の議論は PubMed 不使用に伴い**本サーベイでは無効**(適用対象DBが無い)。
  今後の rule.md 改訂で MeSH 関連の記述は削除してよい。
- §D(フィルタ層)・方針2(TA基準)・方針3(degradeフラグ)・方針5(Known-Item Test)は
  **DB数によらず妥当**であり Rev.8 でもそのまま継続。

### 著者確認事項の更新(Rev.7 からの差分)

- `outputs/pubmed_unique_175.csv` の30件 judge_relevance 判定: **優先度を格下げ**
  (PubMed不使用が確定したため、DB選定の意思決定には不要。実施する場合も
  「参考記録」の位置づけ)。
- 心理接合点 background 文献(#19 Botvinick & Cohen 1998、#20 Lenggenhager 2007)は、
  PsycINFO正当化ドラフトの「スノーボーリングで残余リスクを緩和する」主張と接続する
  境界文献としても機能する(`self_scale_references.csv` に追加済み、`known_items.md` 参照)。

### 2026-07-27 補足: Scopus scope の実測(TITLE-ABS vs TITLE-ABS-KEY)

`scripts/db_search_scopus.py`(Rev.6第2波再検索の自動化ツール、Scopus Search API 経由)による
`--count-only` 実測で、§D で「要著者確認」のままだった Scopus のフィールドscope(TITLE-ABS か
TITLE-ABS-KEY か)に高確度の証拠が得られた。

| クエリ | scope | 件数 | 備考 |
|---|---|---|---|
| 旧クエリ(初回検索、G1未拡張) | 不明(要確認だった) | **4,331** | Rev.3時点の記録値(`search_strings.md`) |
| Rev.6 G1拡張クエリ | `TITLE-ABS`(Rev.7/8のTA方針) | **2,533** | 実測(2026-07-27) |
| Rev.6 G1拡張クエリ | `TITLE-ABS-KEY` | **4,727** | 実測(2026-07-27) |

**解釈:** G1拡張は語のOR追加のみであり、件数は同scope内で単調増加するはずである
(集合として真に拡大するため減ることはない)。にもかかわらず拡張後の `TITLE-ABS`(2,533)が
旧クエリの記録値(4,331)を大きく下回る一方、拡張後の `TITLE-ABS-KEY`(4,727)は
旧クエリの記録値をやや上回り整合する。**旧初回検索は実際には `TITLE-ABS-KEY` で
実行されていた可能性が高い**という結論になる(完全な証明ではない — 2026-05-15時点との間の
Scopus索引自体の増分という別要因も理論上あるが、影響は小さいと考えられる)。

**決定(著者確認・2026-07-27):** この実測を踏まえても **TA基準(TITLE-ABS)を維持**する
(Rev.7/8の方針を変更しない)。ただし以下を Threats to Validity に明記する:
- 初回検索(旧4,331件)は Keyword を含む広いscopeだった可能性が高く、**今回のTA基準は
  それよりも狭い**(実測: 同一G1拡張クエリで -46%、2,533 vs 4,727)。
- したがって「Scopus の recall が初回検索と比べて低下する」ことは**scope方針変更の意図された
  帰結**であり、検索式やDBカバレッジの欠陥ではない。
- 索引語(Keyword)経由でのみ捕捉されていた文献が、TA限定では構造的に落ちる可能性がある。
  この残余は `snowballing_protocol.md` のスノーボーリングで緩和する対象に含める。
- `search_strings.md` の Scopus 行を更新済み(旧「要著者確認」に本実測を追記)。

## 判断保留・要データ(現時点で確定しない項目)

- Title+Abstract 統一の ACM 適用(→ Abstract 再取得の可否待ち)。
- Rev.6 拡張クエリ第2波投入後の step0 recall 再測定(→ 再検索実施待ち。現 69.2% は
  4DBデータでの測定値。3DB体制での再測定が必要。PubMed経由でのみ捕捉された known-item は
  無いため recall には影響しない見込みだが、実測で確認する)。
- PsycINFO 非索引の残余リスクの定量評価(→ 本レビュー範囲外、スノーボーリングで部分緩和)。

> ~~方針4 の MeSH corpus 便益~~ / ~~PubMed の独立正当化~~ → **Rev.8 で対象外に確定**
> (PubMed 不使用のため判定不要になった。上記「Rev.7分析の位置づけ」参照)。
