# Search Replication Protocol — 検索記録の復元・再実行の手順書

> **【Rev.8 確定(2026-07-22)】DB構成は3DB(ACM/IEEE/Scopus)。PubMed は不使用、
> PsycInfo はアクセス制約により従来どおり不使用。** 以下の PubMed(§3)・PsycInfo(§5)の
> 手順は**経緯として保存**し削除しない(初回検索は実施済みの事実であり監査の裏付けデータとして残す)。
> 第2波再検索(Option B)は **ACM / IEEE / Scopus の3DBのみ**を対象に実施する。
> 詳細は `protocol_changelog.md` Rev.8、正当化は `methodology_decision_Rev7.md` §Rev.8追記を参照。

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
- **判断**: 充足率が高ければフィルタ層の scope を TA+K に格上げし、その旨を次改訂(Rev.9候補)として記録。
  Keyword が Scopus でしか揃わないなら、K は「Scopus のみ有効・ACM/IEEE は degrade」で報告する
  (Rev.8 で3DB体制に確定。ACM/IEEE の Keyword 列は使えないため、K の全DB統一は依然不可)。

### 欠陥3: verbatim フィールド指定構文の未記録

各DBで実際に **どのフィールドに検索をかけたか**(Scopus: `TITLE-ABS` か `TITLE-ABS-KEY` か /
ACM: `Title:`/`Abstract:` の指定 / IEEE: `"Document Title":`/`"Abstract":`。~~PubMed: `[tiab]` か `[tw]` か~~
は Rev.8 不使用確定により対象外)は
`search_strings.md` の「Fields searched」欄で **「要著者確認」のまま**である。これは実効 scope の
**非対称の源泉**であり、フィルタ層で何を「正規化して揃える」のかの基準になる。→ §運用ルール参照。

## Option B: 再検索(verbatim 検索式の確定が必要な場合のみ)

以下は再検索を行う場合の手順。目的: (1) DB別 verbatim 検索式・実行日・ヒット数の確定記録、(2) DB別生データの保全。
再実行後は `search_strings.md` の表を全て埋め、DB別エクスポートファイルを `raw/` に保存すること。

> **【2026-07-22 追記】IEEE / Scopus は API 経由で自動化できる。** ACM Digital Library には
> 一般利用可能な検索APIが無いため、ACM は引き続き本節の手順で手動エクスポートする。
> IEEE Xplore Metadata API・Scopus Search API を使う場合は、以下のスクリプトが
> Rev.6 拡張クエリ(G1コンセプト群)を各DBのフィールド指定構文に機械的に変換し、
> ページング・RIS出力・実行記録まで行う(**外部API通信のため著者が実行**、Claude は実行しない):
>
> - `scripts/api_search_common.py` — 共通部品(クエリビルダー・HTTP再試行・RIS出力・実行ログ)
> - `scripts/db_search_ieee.py` — IEEE Xplore Metadata API(要 `IEEE_API_KEY`、developer.ieee.org で無料登録)
> - `scripts/db_search_scopus.py` — Scopus Search API(要 `SCOPUS_API_KEY`、dev.elsevier.com で登録。
>   Abstract/Keyword まで取るには機関アクセスまたは `SCOPUS_INSTTOKEN` が要る場合が多い)
>
> 出力は `raw/{ieee,scopus}_wave2_YYYYMMDD.ris`(Zotero に直接インポート可)。
> インポート後は本ページ §Option A の手順どおり専用コレクションからCSVエクスポートし、
> `search_strings.md` の DB別記録表に実行記録(`outputs/api_search_log.csv`)を転記する。
> 詳細・注意点は各スクリプトの docstring を参照(フィールド名がAPIバージョンで変わりうるため、
> 少数件での試験実行を必ず挟むこと)。

> **注意:** 再検索すると DB 更新により件数は 2025-12/2026-05 実行時と必ずズレる。
> 既存パイプライン(14,385件系列)の数値を置き換えるか、「検索式確認のための監査再実行」として
> 別記録にするかを事前に決め、protocol_changelog.md に記録すること。

## 共通ルール(Option B)

1. **検索は全DBを同じ日(可能なら同日中)に実行**し、日付を記録する(DB更新による件数変動を避ける)。
2. 統合クエリ(`search_strings.md` 冒頭)を各DBの構文へ翻訳して用いる。**実行した文字列をそのままコピーして記録**する(手で整形しない)。
3. フィルタ(期間・文献タイプ・言語)は原則使用しない。使った場合は必ず記録する。
4. **エクスポート直後のヒット数**をDBの画面表示から記録し、**エクスポートされた実件数と突き合わせる**。
   両者が一致しない場合は上限による打ち切りなので、年でスライスして取り直す
   (ACM=1,000件・IEEE=2,000件の上限を実測で確認済み)。
   検証は `python -X utf8 scripts/export_completeness_audit.py` で機械的に行う。
5. DB別の生エクスポートは加工せず `raw/` ディレクトリに保存: `raw/acm_YYYYMMDD.csv` など。**統合前のファイルを必ず残す**(今回の再実行の主目的)。
6. Zotero への取り込みは「DB別に別コレクション」で行い、`Library Catalog` 列が埋まる取り込み方法(Translator経由)を優先する。CSVエクスポート時に取得元を失わないよう、**取り込み前に各レコードへ取得元DBを示すタグ(例: `src:acm`)を付与**する。

## DB別手順

### 1. ACM Digital Library (dl.acm.org)

> **⚠️ 2026-08-02 の失敗事例(必読)。** 3群をまとめた1本のクエリを投げたところ **81件**しか
> ヒットせず、scope の問題と誤診しかけた。原因は**クエリ構文が効いていなかった**こと。
> Title と Abstract を別々に投げ直すと **6,012件 / 8,328件**で、ACM の Abstract 索引は健全だった。
> さらに、そこからエクスポートした BibTeX 2本が**どちらも 1,000件ちょうどで打ち切られ**、
> しかも**中身が同一**(同じエクスポートの文字コード違い)だった。打ち切りは新しい年に偏っており、
> gold set の ACM 3件のうち2件が欠落していた。**この状態で Known-Item Test を回すと
> 「recall が低い」という誤った結論が出る。**

**(a) クエリ形式 — 和集合方式(Rev.9 時点の決定)**

- Advanced Search →「Edit Query」で、`AllField:` ではなく **`Title:` / `Abstract:` を明示**する
  (`AllField:` は全文検索になり過剰ヒット)。
- **title検索と abstract検索を別々に実行し、和集合を取る。**
  - 理由: 群ごとに `(Title:G OR Abstract:G)` を入れ子にした単一クエリが本来の TA 形だが、
    ACM の Edit Query での可搬性が確認できていないため、確実に実行できる分割方式を採る。
  - **代償(必ず報告する): フィールド横断の一致を取りこぼす。** 「G1 はタイトルに、G2 は要旨にのみ
    出現する」文献は和集合に入らない。gold set 13件中11件が Abstract のヒットに依存しており、
    #8 のような横断ケースが実在するため、これは机上の懸念ではない。
    **PRISMA-S / Threats to Validity に「ACM は Title 検索と Abstract 検索の和集合であり、
    フィールド横断の一致は取りこぼしうる」と明記すること。**
- 「The ACM Guide to Computing Literature」ではなく「**ACM Full-Text Collection**」を
  選択したかを記録する(母集団が変わる)。

**(b) エクスポート — 1,000件上限があるので年でスライスする**

- **ACM DL のエクスポートは 1,000件で打ち切られる**(2026-08-02 実測)。
  打ち切りは黙って起きる(警告が出ない)ため、**件数の突き合わせを必ず行う**。
- 手順:
  1. 検索実行後、**出版年ごとのヒット数を控える**(この表はそのまま PRISMA の記録になる)。
  2. **1スライス < 1,000件**になるよう年をまとめてスライスし、スライスごとにエクスポートする。
     ヒットの多い直近年は1年単位、古い年はまとめてよい。
  3. スライスごとに下表を埋める。**3列目と4列目が一致しないスライスは取り直す。**

     | 検索種別 | 年範囲 | UI表示ヒット数 | エクスポート件数 | ファイル |
     |---|---|---|---|---|
     | title | 2026 | | | |
     | title | 2025 | | | |
     | ... | | | | |
     | abstract | 2026 | | | |

  4. 全スライスを **Zotero の単一コレクション `acm_wave2`** に取り込む
     (title分と abstract分をまとめて入れてよい。重複は Phase 1 の DOI 重複削除で吸収される)。
  5. コレクションを CSV エクスポート → `raw/acm_wave2_YYYYMMDD.csv`。
- 文字コード: UTF-8。ID列: DOI(`10.1145/...`)が主キー。

**(c) 検証(必須)**

```bash
python -X utf8 scripts/export_completeness_audit.py --files raw/acm_wave2_YYYYMMDD.csv \
    --expect acm_wave2=<スライスのUIヒット数合計>
```

打ち切りの疑い・gold set の欠落・期待件数との差があれば警告が出る。**警告が消えるまで先へ進まない。**

### 2. IEEE Xplore (ieeexplore.ieee.org)

- Advanced Search → Command Search で構文指定:
  `("Document Title":... OR "Abstract":...)` 形式。**"All Metadata" は使わない**(出版社名等にもマッチするため)。
- エクスポート: 結果画面 → Export → CSV(上限 2,000件/回。超える場合は年で分割し、分割条件を記録)。
- 文字コード: UTF-8(BOM付きの場合あり — 取り込み時は `utf-8-sig` で読む)。
- ID列: DOI(`10.1109/...`)+ IEEE Document Number。

### 3. PubMed (pubmed.ncbi.nlm.nih.gov) — **Rev.8 により不使用に確定**

> 医学・治療目的の文献が中心で本サーベイのスコープ外・主題適合性が低いため不採用
> (`protocol_changelog.md` Rev.8)。以下は初回検索(2026-05-15 実施済み)の手順記録として保存。
> **第2波以降の再検索対象からは除外する。**

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

### 5. PsycInfo — **不使用(アクセス制約、Rev.5で確定・Rev.8で再確認)**

- アクセス制約により実行不可。旧 rule.md の規定「PubMed での検索が不十分な場合の補完」は
  PubMed 自体が Rev.8 で不使用のため無効。
- 不使用の正当化(Scopus による代替カバレッジ + Known-Item Test での実証)は
  `methodology_decision_Rev7.md` §Rev.8追記の正当化ドラフトを本文・Threats to Validity に転用する。

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
