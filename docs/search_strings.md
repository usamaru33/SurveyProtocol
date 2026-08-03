# Search Strings — データベース別検索式の記録

> PRISMA 2020 Item #7(検索戦略の完全な提示)対応。各DBで実行した検索式を **verbatim**(実行時のコピー&ペースト)で記録する。
>
> **現状の結論(2026-07-16 改訂):** 検索結果は **Zotero で管理されており、取得元DBごとにコレクション(フォルダ)分けされている**(本リポジトリの CSV はその統合エクスポート)。したがって:
> - **DB別ヒット数(PRISMA "Records identified from each database")** → **再検索不要**。Zotero のコレクション別エクスポートで復元可能(手順: `search_replication.md` Option A)
> - **実行日** → CSV の `Date Added` より、取り込みは **2025-12-25(1,276件)と 2026-05-15(13,109件)の2回** と確定。これが検索実行日の上限近似(要著者確認: 2波の経緯 — 予備検索+本検索?)
> - **verbatim 検索式・使用フィルタ** → Zotero には保存されない情報のため、**依然として未記録**。著者の手元記録(検索メモ・ブラウザ履歴・DBアカウントの検索履歴)を確認し、無ければこの項目のみ再実行で確定する

## 実行された統合クエリ(全DB共通、2026-07-17 著者確認により確定)

```
("Virtual Reality" OR "VR" OR "HMD")
AND ("Avatar" OR "Body" OR "Embodiment")
AND ("Size" OR "Scale" OR "Height" OR "Distance")
```

対象フィールド: Title および Abstract(rule.md 記載。各DBでのフィールド指定構文は未記録)。

> **注:** rule.md 旧版に記載されていた詳細クエリ("Virtual Environment" や "Body ownership" 等の
> 複合語を含む)は**計画段階のものであり、実行されていない**(protocol_changelog.md Rev.5)。

## Rev.6 改訂クエリ(2026-07-17 著者確定・再検索は実施待ち)

```
("Virtual Reality" OR "VR" OR "HMD" OR "head-mounted display"
 OR "head mounted display" OR "Virtual Environment*" OR "immersive virtual")
AND ("Avatar" OR "Body" OR "Embodiment")
AND ("Size" OR "Scale" OR "Height" OR "Distance")
```

- G1 のみ拡張(理由は protocol_changelog.md Rev.6)。G2/G3 は初回と同一。
- 再検索を実施したら本表に「(第2波)」行として DB別に verbatim・実行日・ヒット数を追記する。
- 加えて Frontiers in Virtual Reality の supplementary source
  (`search_replication.md` 参照)の実行記録もここに追記する。

> **【Rev.7 運用ルール(必須)】第2波再検索では「Fields searched」を verbatim で必ず記録する。**
> 各DBで実際にどのフィールド構文を使ったかが、フィルタ層(方針3)で「正規化して揃える対象 scope」の
> 基準になる。実効 scope は Rev.7 で **TA(Title-Abstract)を基準**に確定しているため、以下を厳守:
> - **Scopus**: `TITLE-ABS(...)` を使う(`TITLE-ABS-KEY` は索引語まで拾い scope が広がる)。
>   どちらを実行したか画面のクエリ文字列をそのまま貼る。Keyword を回収して TA+K に格上げする場合のみ
>   `TITLE-ABS-KEY` を検討し、その旨を明記。
> - ~~**PubMed**: `[tiab]` を使う~~ **→ Rev.8で不使用確定のため対象外**(MeSH関連の記述も同様に無効)。
> - **ACM**: `Title:` / `Abstract:` を明示(`AllField:` は全文検索で過剰ヒット)。
> - **IEEE**: `"Document Title":` / `"Abstract":`(`"All Metadata"` は不可)。
> 記録先は本表の「Fields searched」列。現在「要著者確認」のままの初回分も、著者の検索履歴から
> 判明したら遡って埋める(判明しなければ「記録なし」と明記し Threats で言及)。

> **【Rev.8 確定(2026-07-22)】DB構成を3DB(ACM/IEEE/Scopus)に確定。PubMed は不使用。**
> 理由・詳細は `protocol_changelog.md` Rev.8、正当化ドラフトは `methodology_decision_Rev7.md` §Rev.8追記を参照。
> 下表の PubMed / PsycInfo 行は**経緯として保存**し削除しない(初回検索は実施済みの事実であり、
> PRISMA の "records identified" には含めないが、Rev.7 分析の裏付けデータとして raw/PubMed.csv も残す)。
>
> **【2026-07-27 実測】Scopus scope の「要著者確認」に高確度の実測証拠。** Scopus Search API で
> 同一クエリ骨格を scope 別に実行した結果: `TITLE-ABS`(Rev.7/8のTA方針どおり)= **2,533件**、
> `TITLE-ABS-KEY` = **4,727件**。旧記録(Rev.3時点、旧G1クエリ)の **4,331件** は、G1拡張後の
> TITLE-ABS(2,533)より少なく矛盾するが、TITLE-ABS-KEY(4,727、旧G1ならさらに少ない適正値になる)
> とは整合する。**旧検索は実際には TITLE-ABS-KEY で実行されていた可能性が高い**という結論。
> 著者確認のうえ **TA基準を維持する方針を再確定**(scopeは変更しない)。詳細・数値の全体は
> `methodology_decision_Rev7.md` §Rev.8追記(2026-07-27補足)を参照。

## DB別記録表

| DB | Search string (verbatim) | Fields searched | Filters | Date executed | Hits |
|---|---|---|---|---|---|
| ACM Digital Library | 統合クエリ(上記)✅ ※ACM構文への翻訳形は未記録 | Title, Abstract(指定構文は**要著者確認**) | **要著者確認** | ≤ 2026-05-15(Zotero取込日) | **7,997** ✅ |
| IEEE Xplore(初回) | 統合クエリ(上記)✅ ※Command Search 構文は未記録 | Title, Abstract(指定構文は**要著者確認**) | **要著者確認** | ≤ 2025-12-25(Zotero取込日) | **1,276** ✅ |
| IEEE Xplore(更新検索) | 統合クエリ(上記)✅ | 同上 | 出版年 2025〜2026 に限定 | 2026-07-17 | **297**(うち初回・他DBと重複しない新規 **101**)✅ |
| ~~PubMed~~ **(Rev.8: 不使用に確定)** | 統合クエリ(上記)✅ ※[tiab] タグの付与形は未記録 | Title/Abstract [tiab](推定、**要著者確認**) | **要著者確認** | ≤ 2026-05-15(Zotero取込日) | 781(初回検索は実施済み。**PRISMA報告からは除外**。主題適合性がスコープ外のため不採用) |
| Scopus | 統合クエリ(上記)✅ ※TITLE-ABS() / TITLE-ABS-KEY() の別は**要著者確認 → 下記2026-07-27実測で高確度判明** | Title, Abstract(**実際は TITLE-ABS-KEY だった可能性が高い、下記参照**) | **要著者確認** | ≤ 2026-05-15(Zotero取込日) | **4,331** ✅ |
| ~~PsycInfo~~ **(Rev.8: 不使用を再確認)** | **未実行が確定**(2026-07-17: Zotero にコレクション無し、アクセス制約のため実行不可)。Rev.8で「Scopus が PsycINFO 収録誌の相当部分を索引しており心理系文献の捕捉は Scopus に依拠する」ことを Known-Item Test で実証(`methodology_decision_Rev7.md` §Rev.8)。不実行の正当化は同ドラフトを本文に転用 | — | — | — | 0(未実行) |

## 第2波(Rev.6 改訂クエリ)の実行記録

| DB | Search string (verbatim) | Fields searched | Filters | Date executed | Hits |
|---|---|---|---|---|---|
| Scopus(第2波) | `TITLE-ABS(("Virtual Reality" OR "VR" OR "HMD" OR "head-mounted display" OR "head mounted display" OR "Virtual Environment*" OR "immersive virtual") AND ("Avatar" OR "Body" OR "Embodiment") AND ("Size" OR "Scale" OR "Height" OR "Distance"))` | TITLE-ABS | なし(view=COMPLETE) | 2026-07-30 | **2,542** ✅ |
| ACM DL(第2波・title検索) | Rev.6 改訂クエリを `Title:` 指定で実行 | Title のみ | 出版年でスライス(下表) | 2026-08-02〜03 | **6,012**(UI表示) / 取得 6,013 |
| ACM DL(第2波・abstract検索) | Rev.6 改訂クエリを `Abstract:` 指定で実行 | Abstract のみ | 出版年でスライス(下表) | 2026-08-02〜03 | **8,328**(UI表示) / 取得 8,331 |
| IEEE Xplore(第2波) | — | `"Document Title":` / `"Abstract":` | — | 未実施 | 379(UI表示のみ、エクスポート待ち) |

> **ACM は Title 検索と Abstract 検索の和集合**(Rev.9 時点の決定、`search_replication.md` §1)。
> **代償: フィールド横断の一致(例: G1 はタイトル・G2 は要旨にのみ出現)を取りこぼす。**
> PRISMA-S / Threats to Validity に逸脱として明記すること。
>
> 取得件数が UI 表示をわずかに上回るのは、エクスポートが数日にまたがったことによる索引の自然増。
> 不足ではないため許容する。**和集合のユニークは 9,630件**(`raw/acm_wave2_20260803.csv`)。

### ACM 第2波のスライス内訳(エクスポート上限1,000件への対応)

ACM DL のエクスポートは**1,000件で打ち切られる**(2026-08-02 実測)。打ち切りは警告なしに起きるため、
出版年でスライスし、1スライスが1,000件未満になるよう分割した。
**元の .bib スライスは `.gitignore` 済み**(Zotero 取り込み後の CSV に集約済み・`scripts/merge_bib.py` で再生成可)なので、
内訳の記録は本表を正とする。

| 系列 | ファイル | 年範囲 | 件数 |
|---|---|---|---|
| title | acm (1) | 2025-2026 | 448 |
| title | acm (2) | 2024-2026 | 629 |
| title | acm (3) | 2024-2025 | 576 |
| title | acm (4) | 2022-2023 | 818 |
| title | acm (5) | 2020-2022 | 685 |
| title | acm (6) | 2017-2019 | 965 |
| title | acm (7) | 2010-2016 | 808 |
| title | acm (8) | 2000-2009 | 875 |
| title | acm (9) | 1989-1999 | 209 |
| | **title 計** | **1989-2026** | **6,013**(ユニーク) |
| abstract | acm (10) | 2026 | 591 |
| abstract | acm (11) | 2025-2026 | 969 |
| abstract | acm (12) | 2024-2025 | 928 |
| abstract | acm (13) | 2023 | 742 |
| abstract | acm (14) | 2022 | 565 |
| abstract | acm (15) | 2021-2022 | 516 |
| abstract | acm (17) | 2016-2018 | 1,000 ★打ち切り |
| abstract | acm (18) | 2010-2015 | 795 |
| abstract | acm (20) | 2005-2009 | 554 |
| abstract | acm (21) | 2019-2021 | 1,000 ★打ち切り |
| abstract | acm (22) | 2017-2018 | 818(★(17)の取り直し) |
| abstract | acm (25) | 2016 | 280(★(17)の取り直し) |
| abstract | acm (26) | 2019 | 533(★(21)の取り直し) |
| abstract | acm (27) | 1973-2004 | 505 |
| abstract | acm (30) | 2020-2021 | 533(★(21)の取り直し) |
| | **abstract 計** | **1973-2026** | **8,331**(ユニーク) |

- ★打ち切りの2本は取り直し版で上書きされているが、他ファイルに含まれない固有レコードを
  持つため保持している(削除するとレコードが減る)。
- 取り直しによる回収実績: 2016 +25 / 2017 +35 / 2018 +38 / 2019 +41 / 2020 +25。
- **1991〜2001年で abstract 検索が title 検索を下回る**のは、当時の ACM 論文に要旨メタデータが
  無いためであり取りこぼしではない(2002年以降は一貫して abstract > title)。

## 確定した PRISMA 上段(2026-07-17、`scripts/raw_db_audit.py` による)

- Records identified: **ACM DL 7,997 / IEEE Xplore 1,276 + 297(更新検索) / PubMed 781 / Scopus 4,331 = 計 14,682**
- 検証(初回検索分): raw 4ファイルと統合CSV(ResearchVR2.csv, 14,385件)は Zotero Key で **1:1 完全一致**(欠落・混入・コレクション重複所属 0件)
- IEEE 更新検索(`raw/IEEE_2025-2026.csv`, 297件): 既存とDOI重複 196件 / 真に新規 **101件**。
  `ResearchVR3.csv`(= ResearchVR2 + 297件)を現行パイプライン入力とし、重複は Phase 1 で除去
- DB間重複(初回分、DOI/正規化タイトル一致、重複除去報告の内訳用):
  PubMed∩Scopus **606** / Scopus∩IEEE **352** / Scopus∩ACM **142** / PubMed∩IEEE **39** / ACM∩IEEE 0 / ACM∩PubMed 0
- 詳細: `outputs/raw_db_audit.csv`

## 未記録項目の明示リスト(2026-07-17 更新)

- ~~verbatim 検索式~~ → **確定済み**(著者提供、上記統合クエリ)。残るのは**各DBでのフィールド指定構文・フィルタの使用有無**のみ(要著者確認、優先度低)。
- ~~DB別ヒット数~~ → **確定済み**(上表 ✅)。
- ~~PsycInfo の実行有無~~ → **未実行が確定**。不実行の判断理由の記載が残タスク。
- ~~検索時点の非対称(IEEE のみ 2025-12 実行)~~ → **解消済み(2026-07-17)**:
  IEEE のみ出版年 2025〜2026 に限定した更新検索を実行し(297件、新規101件)、
  `ResearchVR3.csv` に統合。PRISMA には IEEE の検索を2回(2025-12-25 / 2026-07-17)として報告する。
  なお更新検索の時点で今度は他3DB(2026-05-15)よりIEEEが約2ヶ月新しくなったが、
  差は軽微であり全DBの検索時点を本文に明記することで対応する。

## 現存データから分かること(参考値・PRISMA には使用不可)

統合エクスポート `ResearchVR2.csv`(14,385件)には取得元DB列が無い(`Library Catalog` 全件空欄)。
URL/DOI プレフィックスによる **出版社ベースの推定**内訳は以下の通り:

| 推定出版社 | 件数 |
|---|---|
| ACM (dl.acm.org / 10.1145) | 8,345 |
| Scopus/Elsevier (scopus.com / sciencedirect / 10.1016) | 3,475 |
| IEEE (ieeexplore / 10.1109) | 1,913 |
| Others/Unknown | 650 |
| PubMed/PsycInfo (pubmed / 10.1037) | 2 |

> ⚠️ これは「**どのDBで検索してヒットしたか**」ではなく「**どの出版社の文献か**」の推定である
> (例: Scopus 検索でヒットした ACM 論文は ACM に計上される)。
> PRISMA の "Records identified from each database" としては**報告不可**。再実行時に DB 別件数を必ず記録すること。

---

## 再実行時の記入例(フォーマット)

| DB | Search string (verbatim) | Fields searched | Filters | Date executed | Hits |
|---|---|---|---|---|---|
| Scopus | `TITLE-ABS(("Virtual Reality" OR "VR" OR "HMD" OR "Virtual Environment") AND ("Body ownership" OR "Embodiment" OR "Avatar" OR "Virtual body") AND ("Size perception" OR ...))` | TITLE-ABS | なし(全期間・全文献タイプ) | 2026-XX-XX | n=X,XXX |

*記入ルール: 検索式は実行画面からコピーした文字列をそのまま貼る(手で整形しない)。フィルタを使わなかった場合も「なし」と明記する。*
