# screening/rescreen_bodyshape/ — 体形の論文だけで Phase 3b をやり直す

**Phase 3b(Title/Abstract)の再判定。** 2026-11-19 の MTG で、体形の変化(太る・痩せる)を I_scale に含める方針になった
(`docs/reference/body_shape_scope_analysis.md` §3・§4)。Phase 3b で Exclude にした記録のうち、題名か要旨に体形の語を含む
**61 件**を、新しい規則で 2 名が要旨から判定し直す。方式は Phase 3b と同じ(1 人が Include なら Phase 4 へ)。

| ファイル | 内容 | 追跡 |
|---|---|---|
| `targets.csv` | 対象 61 件と前回の判定(協議リスト内 17 件は最終判定と両評価者の理由、協議リスト外 44 件は stage 2 の第 2 評価者の判定・理由)。**評価者には配らない** | する |
| `rescreen_sheet_<id>.xlsx` | 評価者ごとの判定シート。Phase 3b と同じ書式(判定・除外理由のプルダウン、条件付き書式、記入列以外のロック)。**前回の判定は入れていない** | しない(独立性) |

- 生成: `python -X utf8 scripts/make_bodyshape_rescreen.py`(既存の xlsx は上書きしない。作り直すなら `--force`)。3 人分を作ってあるので、担当の 2 名に配る。
- 対象の選び方: `scripts/trace_body_shape.py` の語のリスト `SHAPE`(事前に固定)に当たり、Phase 3b で落ちたもの(`outputs/body_shape_trace.csv` の stage が「P3b …」)。語が偶然一致しただけの論文も含む。
- 規則: シートの「はじめに」に、`body_shape_scope_analysis.md` §3 の規則の**案**を載せた。MTG で規則(Rev.33)が確定したら、文言を合わせて作り直す(記入前なら `--force`)。
- 集計(未実装): 回収後、`targets.csv` と突き合わせて κ と、Include になった件数を出す。
