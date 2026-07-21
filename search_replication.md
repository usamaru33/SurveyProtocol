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

## Supplementary source: Frontiers in Virtual Reality のカバレッジ確保(Rev.6)

Known-Item Test により、同誌掲載の必須文献3件が現行4DBの検索で捕捉されないことが確認された
(タイトルが検索式に完全適合するのに不在 → 索引欠落が原因。同誌は SJR Q1 のため、
捕捉できれば Phase 2 も通過する)。以下の順で対応する:

1. **Scopus の索引状況を確認**: Scopus の「ソース(Sources)」検索で
   "Frontiers in Virtual Reality" を引き、収載有無とカバレッジ開始年を記録する。
   - **収載されている場合**: Rev.6 クエリでの Scopus 再検索に自然に含まれるため追加作業不要。
     ただし収載開始年より前の巻号は下記 2 の対象。
   - **収載されていない/一部期間のみの場合**: 下記 2 を実施。
2. **誌内検索(journal hand-search)を supplementary source として実施**:
   - Frontiers 公式サイトの誌内検索で Rev.6 クエリ(サイトの構文に翻訳)を実行。
     実行文字列・実行日・ヒット数を search_strings.md に追記する。
   - ヒットを Zotero の専用コレクション(例: `frvir_supplementary`)に取り込み、
     CSV を `raw/frvir_supplementary_YYYYMMDD.csv` として保存。
   - 統合時は他DBと同じ Phase 1 重複削除を通す。
3. **PRISMA 2020 での報告**: この流入は "Records identified from: Databases" ではなく
   **"Identification of studies via other methods" 側(Websites/Organisations/Citation searching
   の行)**で報告する。フロー図の右カラムに `Frontiers in VR journal hand-search (n = X)` を明記し、
   本文の検索戦略節に「索引カバレッジ欠落への対応」として1段落で理由を書く。

## Rev.7 エクスポート欠陥の是正(再検索不要・Zotero 再エクスポートで対応)

> `methodology_decision_Rev7.md` §D が実測した3つのエクスポート欠陥を潰す。
> **いずれも再検索ではなく、既存 Zotero コレクションからの再エクスポート/列選択で解決する**
> (件数は変わらないので PRISMA 上段への影響なし)。フィルタ層(方針3)を TA / TA+K で
> 動かすための前提整備である。

### 欠陥1: ACM の Abstract 欠落(現 4.3% = 342/7,997)

原因の切り分け → 対応の順に:

1. **まず再エクスポートで取れるか確認する。** Zotero の ACM コレクションを開き、数件の
   アイテムで「Abstract」フィールドが Zotero 上に存在するかを見る。
   - **Zotero に Abstract が入っている場合** = CSV エクスポート設定の問題。
     エクスポート時に「Abstract Note」列が含まれる形式(CSV フル/RIS/BibTeX の abstract)で
     出し直す。`raw/acm_zotero_YYYYMMDD.csv` として保存し、充足率を再測定する。
   - **Zotero 自体に Abstract が無い場合** = ACM DL の取り込み時に Abstract が付かなかった。
     ACM DL 側から再取得する:検索結果 → SelectAll → Export Citations で
     **「Include Abstract」相当のオプションを有効にした BibTeX/CSV** を出し、Zotero に再取り込み。
     ACM の Zotero Translator 経由取り込みでも Abstract が入ることが多い。
2. **再取得が不可能な場合のフォールバック**: `scripts/enrich_abstracts.py` を著者が実行し、
   DOI をキーに Crossref → Semantic Scholar から Abstract を補完する
   (外部 API 通信のため Claude は実行しない。コード・手順は同スクリプトの docstring 参照)。
   補完した件数とソースを本文・PRISMA に明記する(再現性のため)。
3. **完了条件**: ACM の `Abstract Note` 充足率を 4.3% から実務的水準(理想 ≥ 95%)へ。
   達成できない残余は「ACM の一部は Title のみで正規化フィルタを適用(degrade)」と PRISMA-S に記載。

### 欠陥2: Scopus の Keyword 欠落(現 1.2% = 51/4,331)

`methodology_decision_Rev7.md` の方針: 実効 scope は当面 **TA(Title-Abstract)**。
Scopus の Author/Index Keywords が回収できた場合に限り **TA+K へ格上げ可**。

- Zotero の Scopus コレクションからの再エクスポートでは Keyword が付かない可能性が高いため、
  **Scopus 本体から再エクスポートする**:検索結果 → Export → CSV で
  **「Citation information + Abstract & keywords」を選択**(`search_replication.md` §4 と同じ設定)。
  これで **Author Keywords** と **Indexed Keywords** の両列が入る。
- `raw/scopus_zotero_YYYYMMDD.csv`(または `raw/Scopus_kw_YYYYMMDD.csv`)として保存し、
  Keyword 列充足率を再測定する。
- **判断**: 充足率が高ければフィルタ層の scope を TA+K に格上げし、その旨を Rev.8 として記録。
  Keyword が Scopus でしか揃わないなら、K は「Scopus/PubMed のみ有効・他DBは degrade」で報告する
  (ACM/IEEE の Keyword 列は使えないため、K の全DB統一は依然不可)。

### 欠陥3: verbatim フィールド指定構文の未記録

各DBで実際に **どのフィールドに検索をかけたか**(Scopus: `TITLE-ABS` か `TITLE-ABS-KEY` か /
PubMed: `[tiab]` か `[tw]` か / ACM: `Title:`/`Abstract:` の指定 / IEEE: `"Document Title":`/`"Abstract":`)は
`search_strings.md` の「Fields searched」欄で **「要著者確認」のまま**である。これは実効 scope の
**非対称の源泉**であり、フィルタ層で何を「正規化して揃える」のかの基準になる。→ §運用ルール参照。

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
