# screening/phase4/ — Phase 4(全文評価)

**Phase 4。** 全文を読んで PICOS で適格性を判定する段階。対象 149 件(`../final/final_decisions.csv` の Include 151 件から重複 2 件を統合)。

| ファイル | 内容 | 追跡 |
|---|---|---|
| `assignment.csv` | 割当表(担当ペア・抽出担当・配布の有無)。均等化 50/50/49 | する |
| `<who>/phase4_sheet_<who>.xlsx` | 各評価者の判定シート(プルダウン)。**他の評価者に見せない** | しない(独立性) |
| `<who>/review_<who>.html` | **閲覧アプリ**(左に全文 PDF、右に記入欄。6 基準を Y/N/? で付けると判定・除外理由が自動で出る)。`make_fulltext_review_app.py` で生成。ブラウザで開く | しない |
| `<who>/progress_<who>.json` | アプリの進捗(S キーで書き出し)。`apply_fulltext_review.py` でシートへ反映する | しない |
| (スマホ) | `serve_review_app.py --id <who>` で同じ Wi-Fi 内に配信。画面は縦 1 列、進捗は PC の `progress_<who>.json` へ自動保存 | しない |
| `<who>/pdf/` | 担当分の全文 PDF(ファイル名は**論文名**。シートの「全文 PDF」列のリンクから開く) | しない |
| `consensus_worklist.csv` | 協議リスト(`score_fulltext.py` が生成) | する |
| `final_decisions.csv` / `extraction_table.csv` | 最終判定 / Include の事実の抽出表(`score_fulltext.py --final`) | する |

手順と基準: `docs/reference/phase4_reviewer_guide.md`。生成・集計: `scripts/make_fulltext_sheets.py` / `score_fulltext.py`。
Phase 3b(Title/Abstract)のファイルは `../stage1/` など。
