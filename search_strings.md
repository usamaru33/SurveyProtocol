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

## DB別記録表

| DB | Search string (verbatim) | Fields searched | Filters | Date executed | Hits |
|---|---|---|---|---|---|
| ACM Digital Library | 統合クエリ(上記)✅ ※ACM構文への翻訳形は未記録 | Title, Abstract(指定構文は**要著者確認**) | **要著者確認** | ≤ 2026-05-15(Zotero取込日) | **7,997** ✅ |
| IEEE Xplore(初回) | 統合クエリ(上記)✅ ※Command Search 構文は未記録 | Title, Abstract(指定構文は**要著者確認**) | **要著者確認** | ≤ 2025-12-25(Zotero取込日) | **1,276** ✅ |
| IEEE Xplore(更新検索) | 統合クエリ(上記)✅ | 同上 | 出版年 2025〜2026 に限定 | 2026-07-17 | **297**(うち初回・他DBと重複しない新規 **101**)✅ |
| PubMed | 統合クエリ(上記)✅ ※[tiab] タグの付与形は未記録 | Title/Abstract [tiab](推定、**要著者確認**) | **要著者確認** | ≤ 2026-05-15(Zotero取込日) | **781** ✅ |
| Scopus | 統合クエリ(上記)✅ ※TITLE-ABS() / TITLE-ABS-KEY() の別は**要著者確認** | Title, Abstract | **要著者確認** | ≤ 2026-05-15(Zotero取込日) | **4,331** ✅ |
| PsycInfo(補完用・条件付き) | **未実行が確定**(2026-07-17: Zotero にコレクション無し)。rule.md の条件「PubMed 検索が不十分な場合の補完」に対し、不実行と判断した理由(PubMed 781件で十分と判断した根拠)を本文に記載すること | — | — | — | 0(未実行) |

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
