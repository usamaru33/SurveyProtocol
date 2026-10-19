# fulltext/ — Phase 4(全文評価)の準備: 全文 PDF の取得

**Phase 4 の入力。** Phase 3b を通過した 149 件の全文 PDF の取得と、その状況の管理。判定そのものは `../screening/phase4/`。

| ファイル | 内容 |
|---|---|
| `manifest.csv` | 対象 149 件の取得状況・出所・DOI。担当ペアの列は仮割当(md5)で、正は `../screening/phase4/assignment.csv` |
| `missing_list.md` / `.xlsx` | 未取得の一覧(`manifest.csv` から作成) |
| `manual_fetch.md` | 手動取得リスト(自動生成。手で編集しない) |
| `excluded_by_consensus.csv` | 対象から外れた記録(協議で Exclude / 同定不能) |
| `duplicates_merged.csv` | 重複で代表に統合した記録 |
| `identification_notes.md` | 書誌の同定の記録 |
| `pdf/`・`by_reviewer/`・`inbox/`・`manual/` | PDF の置き場(著作権のため追跡しない) |

Phase 3b(Title/Abstract)のファイルは `../screening/stage1/` など。
