# screening/rescreen_bodyshape/ — 体形の論文だけで Phase 3b をやり直す

**Phase 3b(Title/Abstract)の再判定。** `rule.md` Rev.33(2026-11-21)で、体形の変化(太る・痩せる)を I のスケール操作に含めた。
Phase 3b で Exclude にした記録のうち、題名か要旨に体形の語を含む **61 件**を、Rev.33 の規則で要旨から判定し直す。

## 手続き(Phase 3b と同じ 2 段、liberal accelerated)

| 段 | 内容 | 件数 |
|---|---|---|
| 第 1 段 | 著者が全件を判定 | 著者 61 |
| 第 2 段 | 著者が Exclude / Unsure にした記録を、第 2 評価者が確認(`--stage2`、著者の記入後) | 著者の判定しだい(割当は `targets.csv` の `second_reviewer`: Kataoka 27 / WATANABE 34 件のうち該当分) |

- Include は 1 人で通す(Phase 4 へ)。2 人とも Exclude で除外。Unsure は第 2 評価者へ回し、決着しなければ協議。
- 第 2 評価者の振り分けは Phase 3b と同じ `second_reviewer_of`(`md5("2nd:"+key)`)。
- **校正セット(κ)は設けない**(2026-11-24、著者の判断。記入前)。基準の運用の一致は Phase 3b 本番の校正で確認済みで、61 件の 20%(13 件)では κ が安定しないため。方法の節では、Phase 3b との違いとしてこの点を書く。
- 経緯: 2026-11-21 に 2 名が全件を読む方式から Phase 3b と同じ 2 段に変更、2026-11-24 に校正セットを外した。どちらも記入前。

## ファイル

| ファイル | 内容 | 追跡 |
|---|---|---|
| `targets.csv` | 対象 61 件の割当(`second_reviewer`)と前回の判定(協議リスト内 17 件は最終判定と両評価者の理由、外 44 件は stage 2 の判定・理由)。**評価者には配らない** | する |
| `rescreen_sheet_author.xlsx` | 第 1 段: 著者(61 件) | しない(独立性) |
| `rescreen_stage2_sheet_<id>.xlsx` | 第 2 段(著者の記入後に `--stage2` で生成)。著者の判定は入れない | しない |

- 生成: `python -X utf8 scripts/make_bodyshape_rescreen.py`(第 1 段)/ `--stage2`(第 2 段)。既存の xlsx は上書きしない。`--force` でも記入済みのセルがあれば止まる。
- 書式は Phase 3b の `make_screening_xlsx.py` をそのまま使う(判定・除外理由のプルダウン、条件付き書式、記入列以外のロック)。前回の判定はシートに入れない。
- 対象の選び方: `scripts/trace_body_shape.py` の語のリスト `SHAPE`(事前に固定)に当たり、Phase 3b で落ちたもの。語が偶然一致しただけの論文も含む。
- 規則: `rule.md` Rev.33。シートの「はじめに」にその文言を載せた。
- 集計(未実装): 回収後、Phase 4 に戻る件数を出す。
