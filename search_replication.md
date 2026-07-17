# Search Replication Protocol — 検索記録の復元・再実行の手順書

> PRISMA 上段("Records identified from each database (n=)")を報告可能にするための手順。
> **検索結果は Zotero で管理されており、取得元DBごとにコレクション分けされている**ため、
> まず Option A(Zotero からの復元・再検索不要)を実施し、
> それでも埋まらない項目(verbatim 検索式等)のみ Option B(再検索)で確定する。

## Option A: Zotero コレクションからの復元(推奨・再検索不要)

DB別ヒット数と DB別生データは Zotero から復元できる。

1. Zotero で各DBのコレクションを開き、**件数を記録**する(右下のアイテム数表示)。
   この件数が PRISMA の "Records identified from each database (n=)" になる。
   - ⚠️ 取り込み後にコレクション内で手動削除・移動をした場合、検索時のヒット数と一致しない。
     心当たりがあれば search_strings.md にその旨を注記する。
2. コレクションごとに右クリック → 「コレクションをエクスポート」→ **CSV(UTF-8)** で
   `SurveyProtocol/raw/` に保存する。ファイル名: `raw/<db名>_zotero_YYYYMMDD.csv`(例: `raw/acm_zotero_20260716.csv`)。
3. 各CSVに取得元DB列が無いため、**ファイル名がDB名の記録を兼ねる**。統合処理を行う場合は
   読み込み時に `Source_DB` 列を付与すること。
4. 検証: DB別件数の合計(DB間重複を含む)が統合エクスポート 14,385件と整合するか確認する。
   - 一致しない場合、統合エクスポート時の範囲(My Library 全体 vs 特定コレクション群)を特定して記録する。
5. `search_strings.md` の Hits 列と Date executed 列(Zotero の `Date Added`: 2025-12-25 / 2026-05-15 の2波)を埋める。
6. 完了後、`scripts/known_item_test.py` の step0 を「DB別生データでの存在判定」に拡張できる
   (どのDBの検索式が既知文献を拾ったかまで特定可能になる)。

**Option A で埋まらないもの:** verbatim 検索式・使用フィルタ(Zotero には保存されない)。
著者の手元記録(検索メモ・DBアカウントの検索履歴・ブラウザ履歴)を先に確認し、無ければ Option B へ。

## Option B: 再検索(verbatim 検索式の確定が必要な場合のみ)

以下は再検索を行う場合の手順。目的: (1) DB別 verbatim 検索式・実行日・ヒット数の確定記録、(2) DB別生データの保全。
再実行後は `search_strings.md` の表を全て埋め、DB別エクスポートファイルを `raw/` に保存すること。

> **注意:** 再検索すると DB 更新により件数は 2025-12/2026-05 実行時と必ずズレる。
> 既存パイプライン(14,385件系列)の数値を置き換えるか、「検索式確認のための監査再実行」として
> 別記録にするかを事前に決め、protocol_changelog.md に記録すること。

## 共通ルール(Option B)

1. **検索は全DBを同じ日(可能なら同日中)に実行**し、日付を記録する(DB更新による件数変動を避ける)。
2. 統合クエリ(`search_strings.md` 冒頭)を各DBの構文へ翻訳して用いる。**実行した文字列をそのままコピーして記録**する(手で整形しない)。
3. フィルタ(期間・文献タイプ・言語)は原則使用しない。使った場合は必ず記録する。
4. **エクスポート直後のヒット数**をDBの画面表示から記録する(エクスポート上限で件数が欠ける場合はその旨も記録)。
5. DB別の生エクスポートは加工せず `raw/` ディレクトリに保存: `raw/acm_YYYYMMDD.csv` など。**統合前のファイルを必ず残す**(今回の再実行の主目的)。
6. Zotero への取り込みは「DB別に別コレクション」で行い、`Library Catalog` 列が埋まる取り込み方法(Translator経由)を優先する。CSVエクスポート時に取得元を失わないよう、**取り込み前に各レコードへ取得元DBを示すタグ(例: `src:acm`)を付与**する。

## DB別手順

### 1. ACM Digital Library (dl.acm.org)

- Advanced Search → 「Edit Query」で以下の構文を使用:
  `Title:(...) OR Abstract:(...)` の組み合わせ。ACM は Title+Abstract の複合指定が煩雑なため、
  クエリシンタックス例: `AllField:` ではなく `Title:` / `Abstract:` を明示すること(AllField は全文検索になり過剰ヒット)。
- 「The ACM Guide to Computing Literature」ではなく「**ACM Full-Text Collection**」を選択したかを記録。
- エクスポート: 検索結果ページ → Export Citations → **BibTeX または CSV**。
  - 上限: 1ページ単位のエクスポートになる場合あり。全件取得の方法(SelectAll→Export)と取得件数の一致を確認。
  - 文字コード: UTF-8。
- ID列: DOI(`10.1145/...`)が主キー。

### 2. IEEE Xplore (ieeexplore.ieee.org)

- Advanced Search → Command Search で構文指定:
  `("Document Title":... OR "Abstract":...)` 形式。**"All Metadata" は使わない**(出版社名等にもマッチするため)。
- エクスポート: 結果画面 → Export → CSV(上限 2,000件/回。超える場合は年で分割し、分割条件を記録)。
- 文字コード: UTF-8(BOM付きの場合あり — 取り込み時は `utf-8-sig` で読む)。
- ID列: DOI(`10.1109/...`)+ IEEE Document Number。

### 3. PubMed (pubmed.ncbi.nlm.nih.gov)

- 検索ボックスに `[tiab]` タグ付きで入力:
  例 `("virtual reality"[tiab] OR "VR"[tiab] OR ...) AND (...) AND (...)`。
  実行後、「Advanced」→ History からクエリの正規形をコピーして記録。
- エクスポート: Send to → Citation manager(.nbib)または Save → CSV。
  - .nbib は Zotero 直接取り込み可で `Library Catalog=PubMed` が入るため**推奨**。
- ID列: PMID(DOIが無いレコードがあるため、PMID を Extra 列に保持すること)。

### 4. Scopus (scopus.com)

- Advanced search で `TITLE-ABS(...)` を使用。**`TITLE-ABS-KEY` を使うと索引語(Indexed keywords)にもマッチして
  件数が大きく増える**ため、rule.md の「Title/Abstract 対象」に合わせるなら `TITLE-ABS` を使い、どちらを使ったか必ず記録。
- エクスポート: CSV(「Citation information + Abstract & keywords」を選択、上限 2,000件/回 — 超える場合は年分割)。
- 文字コード: UTF-8。
- ID列: EID(`2-s2.0-...`)+ DOI。**Scopus は ACM/IEEE 文献も索引しているため、DOI による重複が必ず発生する**(下記参照)。

### 5. PsycInfo(条件付き)

- rule.md の規定: PubMed での検索が不十分な場合の補完。再実行時に PubMed のヒット内容を確認してから
  実行要否を判断し、**実行しない場合も「実行しない判断とその理由」を search_strings.md に記録**する。

## 重複ID列の扱い(統合時)

1. 各DBエクスポートに **取得元DB列(`Source_DB`)を追加してから**統合する(今回の教訓: 統合後は復元不能)。
2. 重複検出は現行 `pipeline.py` Phase 1 と同一基準(DOI → Key → 正規化タイトル)。
   ただし PRISMA 報告用に「**DB間重複**(同一文献が複数DBでヒット)」と「**DB内重複**」を区別してカウントする。
3. DOI の表記ゆれに注意: 大文字小文字・`https://doi.org/` プレフィックス・末尾ピリオドを正規化してから照合
   (`scripts/known_item_test.py` の `norm_doi()` と同一処理)。
4. PMID/EID など DB固有IDは削除せず Extra 列に温存する(後段の引用数取得・全文入手で使う)。

## 完了チェックリスト(Option A / B 共通)

- [ ] `search_strings.md` の表が5行とも完記(「要著者確認」「REQUIRES RE-RUN」が残っていない)
- [ ] `raw/` にDB別生ファイルが保存されている(加工なし・取得日入りファイル名)
- [ ] DB別ヒット数の合計と統合前レコード数(14,385)の関係が説明できる(DB間重複を含む/含まない)
- [ ] PRISMA フロー図上段(identified / duplicates removed)が新数値で更新されている
- [ ] 旧データ(ResearchVR2.csv 系列)との差分を確認し、差分理由(DB更新・検索式差)を protocol_changelog.md に記録
- [ ] known_items.md の Known-Item Test を新データで再実行(`scripts/known_item_test.py`)
