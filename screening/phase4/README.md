# screening/phase4/ — Phase 4(全文評価)

**Phase 4。** 全文を読んで PICOS で適格性を判定する段階。対象 149 件(`../final/final_decisions.csv` の Include 151 件から重複 2 件を統合)。

| ファイル | 内容 | 追跡 |
|---|---|---|
| `assignment.csv` | 割当表(担当ペア・抽出担当・配布の有無)。均等化 50/50/49 | する |
| `<who>/phase4_sheet_<who>.xlsx` | 各評価者の判定シート(プルダウン)。**他の評価者に見せない** | しない(独立性) |
| `<who>/pdf/` | 担当分の全文 PDF(ファイル名は**論文名**。シートの「全文 PDF」列のリンクから開く) | しない |
| `consensus_worklist.csv` | 協議リスト(`score_fulltext.py` が生成) | する |
| `final_decisions.csv` / `extraction_table.csv` | 最終判定 / Include の事実の抽出表(`score_fulltext.py --final`) | する |

手順と基準: `docs/reference/phase4_reviewer_guide.md`。生成・集計: `scripts/make_fulltext_sheets.py` / `score_fulltext.py`。
Phase 3b(Title/Abstract)のファイルは `../stage1/` など。
