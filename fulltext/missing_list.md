# Phase 4 全文: 未取得リスト(最新版)

作成日: 2026-10-17 / 更新: 2026-10-19(Rev.28 を反映、`R25b5bab30` 取得を反映)

対象は **149 件**(協議 2 回目の最終判定で Include の 151 件から、重複 2 件を代表に統合)。
取得済み 148 件、**未取得 1 件**。一覧は `fulltext/manifest.csv` から作成した(手で編集しない)。

| 分類 | 件数 |
|---|---|
| 取得不要の見込み | 1 |

**あなたの手が要る取得は無い。** 残る `Rbe2e9ecd2` は書誌の確認だけ。

## 取得不要の見込み

- [ ] `Rbe2e9ecd2` MATEC Web of Conferences — DOI なし(担当 author×kataoka、協議 —)
  - 論文ではなく MATEC Web of Conferences(2017)の会議録序文。Exclude の見込みだが、協議での判定は未確認

---

## 2026-10-19 に取得済みへ移した 11 件

- [x] `R25b5bab30` Kim ら, Impact of Body Size Match to an Avatar(担当 author×watanabe)— `manual/Impactofbodysizematchtoanavataronthebodyownershipillusionanduserssubjectiveexperience.pdf`(8 ページ、書誌を照合済み)
- [x] `R83118528e` Wraga 1999, JEP:HPP 25(2)(担当 author×kataoka)— `manual/1999-10532-014.pdf`
- [x] `R5c8c33de9` Dixon ら 2000, JEP:HPP 26(2)(担当 author×kataoka)— `manual/2000-08159-009.pdf`
- [x] `R247a1be9c` Yamamoto ら 2025, Avatar Identity and Conversation on Personal Space(担当 kataoka×watanabe)— `manual/29_29.pdf`。取得済みと誤っていた件(arXiv 2603.06030 は別論文)の訂正済み
- [x] `R272b2107d` Warren & Whang 1987, JEP:HPP 13(3)(担当 author×watanabe、協議 Include)— `manual/1987-33380-001.pdf`
- [x] `R900efbdfe` Phenomenal regression to the real object(担当 kataoka×watanabe)— `manual/Phenomenal_regression_to_the_r.pdf`
- [x] `Rf66443472` Body size illusions influence perceived size of objects(担当 author×kataoka)— `manual/Body_size_illusions_influence_perceived_size_of_ob.pdf`
- [x] `R90145a337` Marklund 2017(KTH 学生論文)(担当 kataoka×watanabe、協議 Include)— `manual/FULLTEXT01.pdf`
- [x] `R4133f7f22` Murcia-López 2018(UCL 博士論文、157 ページ)(担当 author×watanabe、協議 Include)— `manual/Murcia Lopez_10063411_thesis.pdf`
- [x] `Rbd45fc72f` Willemsen & Gooch 2002, IEEE VR(2 ページ、pp.275-276)(担当 author×watanabe、協議 Include)— `manual/vr2002_willemsen_distance.pdf`。**それまで `pdf/` と担当者フォルダに入っていた PDF は別の論文(高齢者向け AR/VR の scoping review)だったので差し替えた**(旧ファイルは退避済み)
- [x] `Rb3c541a72` Bhargava ら VR 2020(10 ページ)(担当 author×watanabe)— `manual/Comparative_Evaluation_of_Viewing_and_Self-Representation_...pdf`。重複の代表(下記)

いずれも PDF 冒頭で書誌を照合し、`scripts/sort_fulltext_inbox.py` で `pdf/<ID>.pdf` と担当者フォルダへ配置、`manifest.csv` を更新した。

## 2026-10-19 に統合した重複 2 組(`duplicates_merged.csv`)

代表の選び方: DB 由来で DOI が正しい側。

| 代表(評価する) | 統合した記録(評価しない) | 論文 |
|---|---|---|
| `Rb3c541a72`(10.1109/vr46266.2020.00073) | `R3d28d9842`(DOI が不正な形式、文献追跡由来) | Bhargava ら VR 2020, passability affordances |
| `Rdf3e2d120`(10.1109/vr.2019.8797787) | `R8e3a14279`(DOI なし、題名に機関名が付いた記録) | The effect of hand size and interaction modality on the virtual hand illusion |

`R8e3a14279` の PDF は `pdf/` に残してあるが、担当者フォルダ(`by_reviewer/`)のコピーは外した。

## 2026-10-19 に著者が Exclude と決めた 1 件(`excluded_by_consensus.csv` へ移動)

- `Rcfe9667f4` 「H5 - Users who spend more time in Giant mode will show a stronger under-estimation effect」(担当 author×kataoka。協議 2 回目では Include)
  - 文献追跡で参考文献リストが壊れて取り込まれた仮説文の断片で、**元の論文を同定できない**。Superman vs Giant(Piumsomboon ら 2018)の PDF を確認したが、この文は無かった。全文を判定できないため Exclude とした。
  - `final_decisions.csv` を Include → Exclude に変更(Include 151 / Exclude 298)。

## 対象から外れた(協議で Exclude になった)17 件

取得済み 16 件と、Gibson 1979(`R746b5156f`、未取得のまま取得不要)。PDF は `fulltext/pdf/` に残してあるが、Phase 4 の対象ではない。
(上の `Rcfe9667f4` を加えると、`excluded_by_consensus.csv` は 18 行。)
