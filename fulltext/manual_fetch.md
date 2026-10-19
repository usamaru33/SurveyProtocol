# Phase 4 手動取得リスト

`scripts/fetch_fulltext.py` が manifest.csv から自動生成する。手で編集しない。
**作業用ツール `python -X utf8 scripts/fulltext_desk.py` を使うのが楽**(ブラウザで一覧が開き、
Enter で出版社ページを開く → PDF を受け箱に保存すると自動で振り分けて次へ進む)。

ツールを使わない場合: ブラウザで開いて保存した PDF(ファイル名はそのままでよい)を `fulltext/inbox/` に入れ、
`python -X utf8 scripts/sort_fulltext_inbox.py` を実行すると、中身で照合して record_id に振り分け、
担当者フォルダへ配り、このリストを更新する。照合できなかったファイルは受け箱に残る
(`--assign "ファイル名=record_id"` で手動指定)。出版社サイトの一括・自動ダウンロードは規約違反になるので行わない。

未取得 2 件

## その他(1 件)

- [ ] `R25b5bab30` Impact of Body Size Match to an Avatar on the Body Ownership Illusion and User's Subjective Experience — [10.1089/cyber.2019.0136](https://doi.org/10.1089/cyber.2019.0136)(author×kataoka)

## DOI なし(書誌の確認が先)(1 件)

- [ ] `Rbe2e9ecd2` MATEC Web of Conferences — DOI なし(author×kataoka)
