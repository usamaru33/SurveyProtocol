# Phase 4 手動取得リスト

`scripts/fetch_fulltext.py` が manifest.csv から自動生成する。手で編集しない。
**作業用ツール `python -X utf8 scripts/fulltext_desk.py` を使うのが楽**(ブラウザで一覧が開き、
Enter で出版社ページを開く → PDF を受け箱に保存すると自動で振り分けて次へ進む)。

ツールを使わない場合: ブラウザで開いて保存した PDF(ファイル名はそのままでよい)を `fulltext/inbox/` に入れ、
`python -X utf8 scripts/sort_fulltext_inbox.py` を実行すると、中身で照合して record_id に振り分け、
担当者フォルダへ配り、このリストを更新する。照合できなかったファイルは受け箱に残る
(`--assign "ファイル名=record_id"` で手動指定)。出版社サイトの一括・自動ダウンロードは規約違反になるので行わない。

未取得 14 件

## その他(5 件)

- [ ] `R247a1be9c` Effects of Avatar Identity (AI or Human) and Conversation on Personal Space in Virtual Reality — [10.20668/adada.29.s1_29](https://doi.org/10.20668/adada.29.s1_29)(kataoka×watanabe)
- [ ] `R25b5bab30` Impact of Body Size Match to an Avatar on the Body Ownership Illusion and User's Subjective Experience — [10.1089/cyber.2019.0136](https://doi.org/10.1089/cyber.2019.0136)(author×kataoka)
- [ ] `R272b2107d` Visual guidance of walking through apertures: body-scaled information for affordances. — [10.1037/0096-1523.13.3.371](https://doi.org/10.1037/0096-1523.13.3.371)(author×watanabe)
- [ ] `R5c8c33de9` Eye height scaling of absolute size in immersive and non-immersive displays — [10.1037/0096-1523.26.2.582](https://doi.org/10.1037/0096-1523.26.2.582)(author×kataoka)
- [ ] `R83118528e` Using eye height in different postures to scale the heights of objects. — [10.1037/0096-1523.25.2.518](https://doi.org/10.1037/0096-1523.25.2.518)(author×kataoka)

## DOI なし(書誌の確認が先)(5 件)

- [ ] `R4133f7f22` The effectiveness of training in virtual environments — DOI なし(author×watanabe)
- [ ] `R90145a337` Perception of Characters in VR: How a character’s height affects the perception of that character — DOI なし(kataoka×watanabe)
- [ ] `Rbd45fc72f` Proc. IEEE Virtual Reality, 275--276 — DOI なし(author×watanabe)
- [ ] `Rbe2e9ecd2` MATEC Web of Conferences — DOI なし(author×kataoka)
- [ ] `Rcfe9667f4` H5 - Users who spend more time in Giant mode will show a stronger under-estimation effect — DOI なし(author×kataoka)

## IEEE(2 件)

- [ ] `R3d28d9842` Comparative Evaluation of Viewing and Self-Representation on Passability Affordances to a Realistic Sliding Doorway in Real and Immersive Virtual Environments — [10.1109/vr46266.2020.1581293987781](https://doi.org/10.1109/vr46266.2020.1581293987781)(kataoka×watanabe)
- [ ] `Rb3c541a72` Comparative evaluation of viewing and self-representation on passability affordances to a realistic sliding doorway in real and immersive virtual environments — [10.1109/vr46266.2020.00073](https://doi.org/10.1109/vr46266.2020.00073)(author×watanabe)

## Springer(2 件)

- [ ] `R900efbdfe` Phenomenal regression to the real object in physical and virtual worlds — [10.1007/s10055-014-0257-x](https://doi.org/10.1007/s10055-014-0257-x)(kataoka×watanabe)
- [ ] `Rf66443472` Body size illusions influence perceived size of objects: a validation of previous research in virtual reality — [10.1007/s10055-019-00402-z](https://doi.org/10.1007/s10055-019-00402-z)(author×kataoka)
