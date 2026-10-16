# Phase 4 全文取得: 書誌の同定メモ

`manifest.csv` の DOI 欄が空だった論文の同定結果。読み取り(OpenAlex・Crossref の公開 API と `outputs/snowballing_log.csv`)
のみで、`screening/` は触っていない。manifest の DOI 補完は `fulltext/` 側だけで、`screening/stage1/assignment.csv` は未更新。

## 2026-10-16

| record_id | 結果 | 根拠 |
|---|---|---|
| R5c8c33de9 | **同定**。Dixon, Wraga, Proffitt & Williams (2000), *JEP: Human Perception and Performance* 26(2), 582–593。DOI `10.1037/0096-1523.26.2.582`。manifest に補完済み。有料(APA)、学内ライセンスで取得 | Crossref |
| Rbe2e9ecd2 | **論文ではない**。Scopus の「Conference review」で、MATEC Web of Conferences(2017)の会議録序文(「The proceedings contain 90 papers」)。全文取得は不要。判定は Exclude(論文ではない)が妥当 | `data/merged/ResearchVR4.csv`(Scopus 2件) |
| R4133f7f22 | UCL 博士論文(Murcia-López, 2018)。UCL Discovery が閲覧のみ・自動アクセス 403。OpenAlex に OA の PDF URL なし。取得は UCL の「Request a copy」、図書館 ILL、著者への依頼。ダウンロード制限の回避はしない | OpenAlex、`snowballing_log.csv`(seed 23 の forward) |
| R90145a337 | **未同定**。2017 年、S2 による文献追跡(seed 8 の forward)で追加。OpenAlex で当たらず | `snowballing_log.csv` |
| Rcfe9667f4 | **未同定**。seed 13(*Does Scaling Player Size Skew…*)の backward で、S2 が文献リストを壊して取り込んだ仮説文の断片とみられる | `snowballing_log.csv` |

R4133f7f22・R5c8c33de9・R90145a337・Rcfe9667f4 は ResearchVR4 には無く、文献追跡で追加された記録(DOI を持たない)。
R90145a337・Rcfe9667f4 は協議2回目の空欄 24 件(#13・#24)にも入っており、全文取得の前に協議で判定が決まる可能性がある。

## 2026-10-16(論文集からの切り出し)

| record_id | 内容 |
|---|---|
| R0ae21cf3e | EuroVR 2017 論文集(LNCS 10700、`978-3-319-72323-5.pdf`)の PDF 133〜147 ページ(章 *Can Virtual Human Entourage Elements…*、本文・参考文献)を切り出して割り当て。論文集本体は `fulltext/manual/` に残してある(git 追跡外) |
