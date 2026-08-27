---
name: survey-pr
description: サーベイのプルリクエストを作成する。「PR作って」「push してPR」と言われたとき、およびブランチの作業を main へ上げる前に使う。PR を出す前に、最新の情報が全ドキュメントへ反映されているかを必ず検証する。
---

# PR 作成前のドキュメント整合性チェック

**PR を作る前に必ずこの検証を通す。** このリポジトリは同じ数値・同じ定義が複数の文書に
重複して書かれており、片方だけ更新して食い違う事故が繰り返し起きている。
PR は「コードが動くか」ではなく **「文書がコードと現実に一致しているか」** を担保する地点。

検証をスキップしてよいのは、変更が単一ファイルに閉じていて数値も定義も動かない場合だけ。

---

## 0. 前提の確認

```bash
git -C SurveyProtocol branch --show-current     # main で作業していないか
git -C SurveyProtocol status -s
git -C SurveyProtocol diff --stat origin/main..HEAD
```

- **main に直接コミットしない。** 必ずブランチを切る。
- 既存ブランチが既に main へマージ済みでないか確認する
  （`git rev-list --left-right --count origin/main...HEAD` の右が 0 ならマージ済みの残骸。
  そこに積まず `origin/main` から新規に切る）。

### ★ 判定シートの混入チェック（毎回必須）

```bash
git -C SurveyProtocol diff --stat origin/main..HEAD | grep -i "sheet_"
```

**評価者の判定シート `sheet_*.csv` / `sheet_*.xlsx` が1件でも出たら PR を作らない。**
3人分がリポジトリに入ると互いの判定が見え、二重スクリーニングの独立性が壊れる
（`.gitignore` で除外済みだが、`git add -f` や新規パスで抜けうる）。
`EXAMPLE_記入見本.*` と `assignment.csv` は追跡対象なので出てよい。

---

## 1. 数値の一貫性

**同じ数値が複数の文書に散っている。** 片方だけ直すと必ず食い違う。
パイプラインを再実行した、判定対象が変わった、件数が動いた場合は全箇所を確認する。

| 数値 | 出てくる場所 |
|---|---|
| PRISMA の各段の件数 | `README.md`・`docs/log/PROGRESS_LOG.md`・`docs/protocol/rule.md`・`docs/log/protocol_changelog.md` |
| Phase 3b の判定対象・内訳 | 上記 + `screening/README.md`・`docs/protocol/screening_protocol.md` |
| 割当件数（校正セット・第2評価者） | `screening/README.md`・`docs/protocol/screening_protocol.md`・`screening/assignment.csv` |
| 要旨欠落・補完件数 | `docs/protocol/screening_protocol.md`・`screening/README.md` |

```bash
cd SurveyProtocol
# 主要な数値がどこに書かれているかを洗う（数値は都度変える）
grep -rnE "1,052|14,682|795|257|191|164" README.md docs/*.md screening/README.md
```

**文書に書かれた数値は、実データに突き合わせて検証する。** 記憶や以前の記述を写さない。

```bash
python -X utf8 -c "
import csv; csv.field_size_limit(10**9)
from collections import Counter
rows=list(csv.DictReader(open('screening/sheet_author.csv',encoding='utf-8-sig')))
print('総件数:', len(rows))
print('取得経路:', dict(Counter(r['source'] for r in rows)))
print('要旨なし:', sum(1 for r in rows if r['has_abstract']=='N'))
print('校正セット:', sum(1 for r in rows if r['calibration']=='Y'))
"
```

> **既知の未更新箇所:** `README.md` §7 の追加分析は旧データ（1,784件時点）のまま。
> 本人が「未更新」と明記しているので、触らないなら注記が残っていることを確認する。
> **消してはいけない。** 未更新であることの表示が消えると、古い数値が現行値に見える。

---

## 2. プロトコル変更が記録されているか

判定基準・体制・DB構成・語彙など**プロトコルに触れる変更は必ず**
`docs/log/protocol_changelog.md` に `Rev.N` として記録する（ACM CSUR の protocol deviations 報告に転用する）。

各エントリに「変更内容 / 変更理由 / 影響範囲」が揃っているか確認する。
**理由は「なぜそれが妥当か」まで書く。** 後で査読者に説明する材料になる。

対応する本体（`docs/protocol/rule.md`）も更新されているか。changelog だけ増えて rule.md が
古いままだと、どちらが正か分からなくなる。

---

## 3. 「正」が1箇所のものが複製とずれていないか

定義の実体が1箇所にあり、他がその写しになっているものがある。**写し側を手で直さない。**

| 正（single source of truth） | 写し |
|---|---|
| `scripts/make_screening_xlsx.py` の `EXCLUDE_REASONS` | xlsx の「はじめに」シート・記入見本・`docs/protocol/screening_protocol.md`・`screening/README.md` |
| `scripts/make_screening_sheets.py` の `REVIEWERS` | 各文書の評価者名 |
| `docs/protocol/rule.md` §5 の参考文献 | 各文書はここを `[R1]` 等で参照する |

語彙や定義を変えたら**再生成して**写しを更新する。

```bash
cd SurveyProtocol
python -X utf8 scripts/make_screening_xlsx.py --force   # 記入済みがあるなら実行しない
python -X utf8 scripts/make_screening_example.py
```

> **再生成の前に記入状況を必ず確認する。** `--force` は記入済みの判定を破棄する。
> ```bash
> python -X utf8 -c "
> import openpyxl
> for n in ['author','kataoka','watanabe']:
>     ws=openpyxl.load_workbook(f'screening/sheet_{n}.xlsx')['判定']
>     print(n, sum(1 for r in range(2,ws.max_row+1) if ws.cell(r,2).value), '件記入済')
> "
> ```
> 1件でも記入されていたら再生成せず、ユーザーに判断を仰ぐ。

---

## 4. 出典が付いているか

方法論上の主張（数値・手法名・「〜という実測がある」）を書いたなら、
**出典は `docs/protocol/rule.md` §5 に集約**し、他文書はそこを参照する。

- 出典なしの数値を新たに増やさない。
- 一次資料を確認できていないものは、**確認できていないと明記**して正式収載しない。
- 引用時の過剰主張の注意（その論文が実際に何を検証したか）も §5 に併記する。

---

## 5. コードのコメント・docstring と実装の乖離

**挙動を変えたら、その関数の docstring と冒頭コメントを読み直す。**
コメントは実行されないので、ずれても誰も気づかない。

```bash
cd SurveyProtocol
git diff origin/main..HEAD -- scripts/ | grep -E "^\+.*(def |# |\"\"\")" | head -30
```

`README.md` に実行手順を載せているスクリプトは、**手順が今も通るか**確認する
（引数名・出力ファイル名・前提ファイルの変更）。

---

## 6. 変更の検証

**「動くはず」で PR を出さない。** 実際に走らせた出力を PR 本文に貼る。

- 集計・検査ロジックを変えたなら、**合成データを作って新しい分岐が発火することを確認**する
  （scratchpad にコピーを作って注入し、本物のシートは触らない）。
- 生成物を変えたなら、生成した実ファイルを開いて中身を検証する。
- 検証していない項目は、PR 本文に**検証していないと書く**。

---

## 7. PR を書く

```bash
gh pr create --base main --head <branch> --title "<title>" --body-file -
```

本文に含めるもの:

- **何を変えたか**と、**なぜそう判断したか**（代替案を採らなかった理由も）
- 実際の検証出力（貼る）
- **レビューで見てほしい点** — 特に主観的な判断（語彙の粒度、基準の解釈など）
- **積み残し・未確認事項** — 隠さない。未確認の出典、古いままの箇所、直せなかったコメント
- 判定データへの影響の有無（「配布前・記入0件」など）

コミットは論理単位で分ける。コミットメッセージ・PR 本文とも日本語でよい。

---

## 8. push と PR は毎回確認を取る

コミットは区切りごとに自律的に行ってよいが、**push と PR 作成はその都度ユーザーの
確認を取る**（`autonomous-commit-authorization` の方針）。

PR を作ったら URL をユーザーに伝え、**含めなかったもの**（未追跡ファイル、
触らなかった箇所）も明示する。

---

## このスキル自体の保守

**スキルファイルも古くなる。** 実際 `survey-pipeline` の SKILL.md は
`ResearchVR2.csv` / 14,385件 / 最終候補1,784件 と書かれたままで、現行の
`ResearchVR4.csv` / 14,682件 / 判定対象1,052件 と食い違っている。

パイプラインの入出力や件数が変わったら、`.claude/skills/` 配下も
チェック対象に含めること。
