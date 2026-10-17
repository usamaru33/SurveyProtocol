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

## 2026-10-17(重複記録 2 組)

同じ論文が、別の record_id で 2 件ずつ記録されている。どちらも DOI の有無・形式の違いで重複排除をすり抜けたとみられる。
**統合は未実施。** 判定(`final_decisions.csv`、凍結中)には触れておらず、扱いは協議で決め、著者の許可を得てから行う。

| 組 | record_id | DOI・題名 | 全文の状態 |
|---|---|---|---|
| A | R8e3a14279 | DOI なし。題名の頭に「University of Birmingham」が付く(機関リポジトリ版の取り込みとみられる) | 取得済み(Birmingham 版) |
| A | Rdf3e2d120 | `10.1109/vr.2019.8797787` | 取得済み(別ファイル。IEEE 版とみられる) |
| B | R3d28d9842 | `10.1109/vr46266.2020.1581293987781`(不正な形式) | **未取得**(PDF は手元にあるが未割当) |
| B | Rb3c541a72 | `10.1109/vr46266.2020.00073`(正しい DOI) | **未取得**(同上) |

- **A**: *The effect of hand size and interaction modality on the virtual hand illusion*(Lin ら、VR 2019)。両 PDF とも 1 ページ目の題名が一致。
  どちらも `final_decisions.csv` で Include(著者 1 名の Include で通過)、担当ペアはどちらも author×kataoka で、同じ 2 人が同じ論文を 2 回判定することになる。
- **B**: *Comparative Evaluation of Viewing and Self-Representation on Passability Affordances to a Realistic Sliding Doorway in Real and Immersive Virtual Environments*(Bhargava ら、VR 2020)。
  `sort_fulltext_inbox.py` が候補 2 件に当たって自動では決められず、PDF 2 ファイル(同一内容)を `fulltext/manual/` に残してある。

### 決めること(協議)

1. 各組で代表の record_id を 1 件決める(DOI が正しい側が自然: A は Rdf3e2d120、B は Rb3c541a72)。
2. もう片方の扱い(Phase 4 の対象から外す / 相互参照だけ残す)。
3. B は、代表を決めてから `--assign` で PDF を割り当てる(未取得 14 → 12 になる)。
4. `final_decisions.csv` の反映は、凍結解除後に著者の許可を得て行う。

## 2026-10-17(未同定 4 件 + 博士論文の調査)

読み取りのみ(Crossref・OpenAlex の公開 API、`outputs/snowballing_log.csv`、`data/pipeline/`)。`screening/` は変更していない。

| record_id | 結果 | 確度・根拠 |
|---|---|---|
| Rbd45fc72f | **同定**。Willemsen & Gooch (2002), *Perceived egocentric distances in real, image-based, and traditional virtual environments*, IEEE VR 2002, pp.275–276。DOI `10.1109/vr.2002.996536`。OA 版なし(IEEE、学内ライセンスで取得)。コーパス内に別の record_id は無い | **高い**。seed 8(Leyrer ら 2011)の Crossref 参考文献に「Willemsen P., *Proc. IEEE Virtual Reality, 275--276*」があり、OpenAlex で著者 Willemsen・同ページの同論文が見つかった |
| R90145a337 | **同定**。Sanna Marklund (2017), *Perception of Characters in VR: How a character's height affects the perception of that character*。学生論文(DiVA、`diva2:1113589`)。OpenAlex は OA 全文なしだが、DiVA は通常 OA | **高い**(題名一致・著者名あり)。DiVA はボット対策の確認ページを返したため自動取得せず、**ブラウザで開いて取得する**。本文を見れば要旨・全文が読める |
| Rcfe9667f4 | **ほぼ同定**。Piumsomboon ら (2018), *Superman vs Giant: A Study on Spatial Perception for a Multi-Scale Mixed Reality Flying Telepresence Interface*, IEEE TVCG。DOI `10.1109/TVCG.2018.2868594`。OA 版なし | **中程度・未確認**。seed 13(Hartman ら 2020)の参考文献にこの論文があり、「Giant mode」の仮説文と整合する。ただし「H5 - …」の文が本文にあるかは未確認(全文が要る) |
| R4133f7f22 | 元になった査読付き論文は**見つけられなかった**(OpenAlex で著者名・題名の検索)。UCL Discovery の「Request a copy」か ILL | 探索は網羅的でない |
| Rbe2e9ecd2 | 変更なし(会議録の序文。全文取得は不要) | — |

### Rcfe9667f4 に関する注意(Phase 3a の再現率)

*Superman vs Giant* は `ResearchVR4.csv` にあり(IEEE、SJR Q1)、**Phase 3a(step 3)のキーワード除外で落ちている**
(`KW_Excl_Category = Cat1 [Not VR / Out of Scope]`、該当語は `mixed reality` と `mr`)。
文献追跡では seed 8・10・13 から 3 回見つかっているが、いずれも `in_db_already = Y`(コーパス内にある)扱いで、
新規候補にはならなかった。つまり**スケール操作(Giant)を扱う論文が、MR を含む語で Phase 3a に落ち、
文献追跡でも拾えていない**。

- 同様の落ち方をした論文が他にもあるかは未確認(step3 除外 384 件のうち、`mixed reality`・`mr` だけで落ちたもの)。
- 方針の変更はしていない(`screening/` は凍結中、プロトコルは rule.md の定義のまま)。
  扱い(例: step3 除外の `mixed reality`/`mr` 単独該当を人手で再確認する)は、著者の判断が要る。

## 2026-10-17(対象を 152 件に変更)

協議 2 回目の最新版(OneDrive 直下、10-13 17:59)で Exclude になった 17 件を `manifest.csv` から外し、対象を 169 → **152 件**にした
(取得済み 139、未取得 13)。外した 17 件は `fulltext/excluded_by_consensus.csv` に、行をそのまま残してある(取得済み 16 件、未取得 1 件 = Gibson 1979)。
PDF 本体(`fulltext/pdf/`・`fulltext/by_reviewer/`)は削除していない。

- **`fetch_fulltext.py` を `--targets` 付きで再実行すると、対象 ID の一覧次第で manifest が上書きされる。** 再実行する場合は 152 件の ID 一覧を渡すこと。
- 対象の最終確定は `final_decisions.csv` の確定後(転記は著者の許可待ち)。校正セットで 3 名全員が Include だった論文は、まだ対象に入っていない。
