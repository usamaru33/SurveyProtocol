# screening/json/ — 閲覧アプリの途中保存

`screening/review_<id>.html` で **`s`** を押すと、判定の途中経過がここへ書き出される。

```
screening/json/progress_author.json     # 著者用（上書き保存）
```

閲覧アプリの判定は普段ブラウザの localStorage にあり、**閲覧データを消すと一緒に消える**
（別PC・別ブラウザにも引き継がれない）。1,052件を読み直さずに済ませる唯一の手段が
このフォルダの JSON なので、作業の区切りごとに `s` を押すこと。

- 読み戻し: 閲覧アプリで **`l`**（このフォルダの `progress_<id>.json`）／
  **`Shift`+`L`**（ファイルを選ぶ）。読み込みは**置き換え**で、実行前に内訳が出る
- 判定シートへの反映:
  `python -X utf8 scripts/apply_review_decisions.py --id author --input screening/json/progress_author.json`
- 初回だけブラウザに保存先フォルダを訊かれる。**このフォルダ（`screening/json`）** を選ぶ

## 形式（`format: "phase3b-progress"`, `version: 1`）

```json
{
 "format": "phase3b-progress",
 "version": 1,
 "sheet": "author",
 "saved_at": "2026-08-31T13:32:42.767Z",
 "fingerprint": "1052:aa71f45",
 "counts": {"done": 201, "include": 33, "exclude": 154, "unsure": 14, "total": 1052},
 "decisions": {
  "Ra3fe11d7d": {"decision": "Exclude", "reason": "スコープ外(主題が無関係)", "note": ""},
  "R4e0697c1a": {"decision": "Include", "reason": "", "note": ""}
 }
}
```

- `sheet` … シートID。**違うシートの進捗は読み込めない**（アプリも反映スクリプトも拒否する）。
  他人の判定を自分のシートへ入れると二重スクリーニングの独立性が壊れるため
- `fingerprint` … `件数:record_id列のSHA-1先頭7桁`。判定対象の集合が同じかを見る。
  違っても読み込めるが警告する（`make_review_app.py` の実行時にも表示される）
- `decisions` … 判定済みのものだけ。並びはシート順（同じ状態なら同じファイルになり diff できる）
- `reason` は Exclude のときだけ入り、値は統制語彙（`make_screening_xlsx.py` の
  `EXCLUDE_REASONS`）に限る。`その他` はメモが必須

**このフォルダの `*.json` は追跡しない**（`.gitignore`）。中身は判定そのもので、
3人分がリポジトリに入ると互いの判定が見えて κ が意味を失うため。
