# Venue 正規化関数の設計見直し提案

> 作成: 2026-07-17。`normalization_collision_audit.py` の実測結果に基づく**提案文書**。
> 実装変更は行っていない(著者判断待ち)。決定後は protocol_changelog.md に記録し、
> pipeline.py を改修のうえ公式再実行すること。

## 1. 現行の正規化仕様(pipeline.py `normalize_venue` の明文化)

入力文字列に対し、次を順に適用する:

1. 小文字化
2. 4桁年号を除去(`\b\d{4}\b`)
3. 序数を除去(`1st`, `22nd` 等)
4. **括弧内テキストを丸ごと除去**(`(VR)`, `(ISMAR)` 等)
5. 非単語文字を空白化
6. **ストップワード除去**(以下の順で正規表現置換):
   `proceedings of` / `proc of` / `proc` / `conference on` / `journal of` /
   `transactions on` / `symposium on` / `international` / `the` / `of` / `on` /
   `in` / `and` / `annual` / `workshop` / `adjunct` / `abstracts` / `workshops` /
   `poster` / `posters`
7. 連続空白を単一化・トリム

さらに照合キー空間には次も投入される:

- CORE: 正規化タイトルに加え **略称の小文字**(`acronym.lower()`)を同一辞書に投入
- SJR: 正規化タイトルに加え **原題の小文字**を投入
- 辞書構築は**ファイル行順の後勝ち**(同一キーは後の行が黙って上書き)
- 照合は **CORE 全段 → SJR** の順(CORE 優先)

## 2. 衝突を生んでいる処理の特定(実測: 衝突899キー / データ出現133キー・489レコード / 採否反転426キー・うちデータ出現74)

| 原因となる処理 | 何が起きるか | 実例(監査で検出) |
|---|---|---|
| **種別語の除去**(`journal of` / `transactions on` / `conference on` / `symposium on` / `workshop`) | ジャーナルと会議、別誌同士が同一キーに融合する | `ACM Transactions on Applied Perception`(SJR Q2誌)と `ACM Symposium on Applied Perception`(CORE B会議)→ 共に `acm applied perception`。`Sensors`(Q1)/`Journal of Sensors`(Q2)/`Sensors International`(Q1)→ 共に `sensors`(19件) |
| **修飾語の除去**(`international` / `annual`) | 別誌が同一キーに融合 | `Psychological Research`(Q1)と `International Journal of Psychological Research`(Q3)→ `psychological research`(6件)。`Annual International Workshop on Presence` → キー `presence` に縮退し、データの `Presence` 誌(29件)を吸引 |
| **後勝ち上書き** | 同一キーの勝者が「CSVの行順」という非本質的要因で決まる | `sensors` キーは Q1 の `Sensors` ではなく後行の `Journal of Sensors`(Q2)が勝ち、Q1誌の論文が Q2 として除外され得る |
| **CORE 優先ポリシー** | ジャーナル論文が同一キーの CORE 会議に吸われる | `IEEE Transactions on Multimedia`(Q1)/`IEEE Multimedia`(Q1)→ `IEEE International Symposium on Multimedia`(CORE C)に照合(10件)。`IEEE Transactions on Image Processing`(Q1)→ CORE B 会議(5件) |
| **略称キーの汎用投入** | 短い正規化キーが CORE 略称と偶発一致し得る | キー空間に `vr` / `mig` / `sap` 等が常駐(データ側 Venue が略称単独のとき誤照合リスク) |
| **段階順序: CORE fuzzy が SJR exact より先** | SJR に正確な収載があっても、CORE 側の低類似ファジーが先に成立して奪う | `Proceedings of the ACM on Human-Computer Interaction`(SJR に **Q2 で正確に収載**)が CORE `Indian Conference on Human-Computer Interaction`(National: India)に fuzzy 照合され除外(**82件** — 単一誤照合として最大。venue_match_audit P1)|
| **積極的正規化 × データ側の短い誌名**(リスト間衝突としては現れないクラス) | リスト内では衝突しないため collision 監査に出ない。venue_match_audit の P2(元文字列類似度低)で捕捉 | データ `Presence` → CORE `Annual International Workshop on Presence`(元文字列類似度 0.35) |

## 3. 改善案とトレードオフ

| 案 | 内容 | 衝突削減 | 表記ゆれ吸収 | 実装コスト | 副作用 |
|---|---|---|---|---|---|
| **案1: 種別マーカー保持** | 正規化時に `journal/transactions/magazine` → `J:`、`conference/symposium/workshop/proceedings` → `C:` をキーへ前置。ジャーナル×会議の衝突クラスを構造的に消す | 大(TAP/SAP型・IEEE Multimedia型を全滅) | ほぼ維持 | 中 | データ側に種別語が無い Venue(`Presence`, `Sensors`)はマーカー不明 → 両タグ試行 or unmatched。J:内・C:内の衝突(`sensors`型の一部)は残る |
| **案2: ストップワード縮小** | 除去対象を「年号・序数・`proceedings of`・冠詞」だけに絞り、`international/annual/workshop/journal of/transactions on` は残す | 大 | **低下**(unmatched 増: 現在の5,119件がさらに増える) | 小 | 表記ゆれの吸収をエイリアス表・ISSN照合へ依存する構造になる |
| **案3: 短キーガード** | 正規化キーのトークン数 ≤ 2 の場合、exact(小文字原題)一致・ISSN一致のみ許可(正規化一致・fuzzy を禁止) | 中(`presence`/`sensors`/`neurology` 型に有効) | 短名Venueのみ低下 | 小 | `CHI` 等の正当な短名照合も unmatched へ → エイリアス表で救済する前提 |
| **案4: 照合後サニティチェック** | どの段階の照合でも、成立後に「元文字列同士の類似度 ≥ 0.60」を要求。未満は unmatched に落として要手動リストへ記録 | 中〜大(全クラスに効く安全網) | 微減 | 小 | 閾値の恣意性 → 採用時は閾値の感度分析(0.5/0.6/0.7 での件数変化)を報告すること |
| **案5: 衝突キーの照合禁止リスト** | 監査で検出済みの衝突899キーを ambiguous として自動照合を禁止し、全てエイリアス表(著者判断)送りにする | 検出済み分は全滅 | 対象キーのみ低下 | 最小 | **リスト内衝突しか対象にできない**(Presence 型は監査に出ない)→ 単独では不完全。データ489レコードが手動判断待ちになる |
| **案6: 照合段階の順序修正** | 「CORE exact → SJR exact(ISSN含む)→ CORE acronym → CORE fuzzy」に並べ替え、**exact を list 横断で fuzzy より常に優先**する | 中(PACM HCI 型 82件を全滅) | 維持 | 小 | CORE と SJR の両方に exact 収載がある会場の優先規則(CORE優先で可)を明文化する必要 |

## 4. 「エイリアス表」vs「正規化関数の修正」— どちらが防御として堅いか

- **エイリアス表(author-verified)**
  - 長所: 1件ずつ著者が確認した対応表であり、**監査可能・Appendix にそのまま掲載可能**。
    再現性の説明が容易(「この表の通り」)。誤修正のリスクが局所化される。
  - 短所: **網羅性の保証がない**。第2波データや将来の再実行で未知の衝突が流入したとき、
    表に無いものは現行ロジックで silent に誤照合される。防御は「既知の敵」にしか効かない。
- **正規化関数の修正**
  - 長所: **クラス単位で系統的に**衝突を殺せる(未知の事例にも効く)。
  - 短所: 修正自体の正しさの検証が必要。吸収力低下により unmatched が増え、
    その処理(エイリアス表送り)が結局必要になる。変更のたびに全数値が動く。
- **結論(提案): 両方を層として使う多層防御**(著者の私見に同意)
  0. **順序修正**(案6)は他の全案と独立に有効で副作用が最小 — 最初に適用すべき
  1. **構造ガード**(案1 種別マーカー + 案3 短キーガード)で衝突クラスを構造的に削減
  2. **安全網**(案4 サニティチェック)で残余クラスを unmatched + 要手動リストへ顕在化
     (silent failure を無くす — 誤照合が「起きたら見える」状態にするのが本質)
  3. **エイリアス表**は最上位のオーバーライドとして維持(著者確認済みの頭を明示的に解決)
  4. **監査2本**(`normalization_collision_audit.py` / `venue_match_audit.py`)を
     パイプライン変更・データ更新のたびの回帰チェックとして常設

## 5. 著者に必要な判断

1. 採用する案の組合せ(推奨: 案1 + 案3 + 案4 + エイリアス表維持)
2. 案3のトークン数閾値(提案: ≤2)/ 案4の類似度閾値(提案: 0.60、感度分析付き)
3. 適用タイミング: **Rev.6 第2波データ統合後の公式再実行に合わせて一括適用**を推奨
   (数値の動く回数を1回に抑え、changelog を Rev.7 として1エントリにまとめる)
