# Search Strings — データベース別検索式の記録

> PRISMA 2020 Item #7(検索戦略の完全な提示)対応。各DBで実行した検索式を **verbatim**(実行時のコピー&ペースト)で記録する。
>
> **現状の結論(2026-07-16 改訂):** 検索結果は **Zotero で管理されており、取得元DBごとにコレクション(フォルダ)分けされている**(本リポジトリの CSV はその統合エクスポート)。したがって:
> - **DB別ヒット数(PRISMA "Records identified from each database")** → **再検索不要**。Zotero のコレクション別エクスポートで復元可能(手順: `search_replication.md` Option A)
> - **実行日** → CSV の `Date Added` より、取り込みは **2025-12-25(1,276件)と 2026-05-15(13,109件)の2回** と確定。これが検索実行日の上限近似(要著者確認: 2波の経緯 — 予備検索+本検索?)
> - **verbatim 検索式・使用フィルタ** → Zotero には保存されない情報のため、**依然として未記録**。著者の手元記録(検索メモ・ブラウザ履歴・DBアカウントの検索履歴)を確認し、無ければこの項目のみ再実行で確定する

## 統合クエリ(概念形、rule.md §3.1 より)

```
("Virtual Reality" OR VR OR HMD OR "Virtual Environment")
AND ("Body ownership" OR Embodiment OR Avatar OR "Virtual body")
AND ("Size perception" OR "Body size" OR "Eye height" OR "Perceived size"
     OR "Spatial scale" OR "Scale perception")
```

対象フィールド: Title および Abstract(rule.md 記載)。

## DB別記録表

| DB | Search string (verbatim) | Fields searched | Filters | Date executed | Hits |
|---|---|---|---|---|---|
| ACM Digital Library | **要著者確認**(手元記録が無ければ REQUIRES RE-RUN) | Title, Abstract(rule.md 記載。ACM での指定方法は未記録) | **要著者確認** | ≤ 2026-05-15(Zotero取込日) | **7,997** ✅ |
| IEEE Xplore | **要著者確認**(同上) | Title, Abstract("Document Title"/"Abstract" 指定の有無は未記録) | **要著者確認** | ≤ 2025-12-25(Zotero取込日) ⚠️他DBより約5ヶ月早い | **1,276** ✅ |
| PubMed | **要著者確認**([tiab] タグ等の実行構文) | Title/Abstract [tiab](推定、未確認) | **要著者確認** | ≤ 2026-05-15(Zotero取込日) | **781** ✅ |
| Scopus | **要著者確認**(TITLE-ABS() / TITLE-ABS-KEY() の別) | Title, Abstract | **要著者確認** | ≤ 2026-05-15(Zotero取込日) | **4,331** ✅ |
| PsycInfo(補完用・条件付き) | **未実行が確定**(2026-07-17: Zotero にコレクション無し)。rule.md の条件「PubMed 検索が不十分な場合の補完」に対し、不実行と判断した理由(PubMed 781件で十分と判断した根拠)を本文に記載すること | — | — | — | 0(未実行) |

## 確定した PRISMA 上段(2026-07-17、`scripts/raw_db_audit.py` による)

- Records identified: **ACM DL 7,997 / IEEE Xplore 1,276 / PubMed 781 / Scopus 4,331 = 計 14,385**
- 検証: raw 4ファイルと統合CSV(ResearchVR2.csv)は Zotero Key で **1:1 完全一致**(欠落・混入・コレクション重複所属 0件)
- DB間重複(DOI/正規化タイトル一致、重複除去報告の内訳用):
  PubMed∩Scopus **606** / Scopus∩IEEE **352** / Scopus∩ACM **142** / PubMed∩IEEE **39** / ACM∩IEEE 0 / ACM∩PubMed 0
- 詳細: `outputs/raw_db_audit.csv`

## 未記録項目の明示リスト(2026-07-17 更新)

- **verbatim 検索式・フィルタ**: 4DB すべてで未記録(Zotero には保存されない情報)。著者の手元記録が無ければ、この項目のみ再実行(`search_replication.md` Option B)で確定する。
- ~~DB別ヒット数~~ → **確定済み**(上表 ✅)。
- ~~PsycInfo の実行有無~~ → **未実行が確定**。不実行の判断理由の記載が残タスク。
- **⚠️ 検索時点の非対称**: IEEE のみ 2025-12-25 実行で、他3DBより約5ヶ月古い。
  2026年前半の IEEE 文献(IEEE VR 2026 等)が捕捉されていない可能性がある。
  対応候補: (a) IEEE のみ同一検索式で更新検索し差分を追加(PRISMAに2回目の検索として記載)、
  (b) カバレッジ期間の非対称を Threats to Validity に明記して許容。

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
