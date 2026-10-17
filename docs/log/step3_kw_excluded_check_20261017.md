# step 3(Phase 3a キーワード除外)384 件の確認: スケール操作を扱う論文が落ちていないか

作成日: 2026-10-17(読み取りのみ。`data/pipeline/` と `screening/` は変更していない)
入力: `data/pipeline/step3_kw_excluded.csv`(384 件)

## きっかけ

*Superman vs Giant*(Piumsomboon ら 2018、`6X75UZKY`)が `mixed reality` / `mr` で step 3 に落ちていた。
同様の論文が他にもあるかを確認した。

## 結果の要約

- 除外理由の内訳(重複あり): Cat3 臨床・医療 242+20+1、Cat1 非 VR・スコープ外 97+20+2、Cat2 技術・非実証 22+2+1。
- **`mixed reality` / `mr` だけで落ちたのは 19 件。うちスケール操作に関わるのは 1 件(`6X75UZKY`)だけ。**
  残り 18 件は MR の応用・システム論文(遠隔協働、ペットのシミュレーション、ロボット操作など)で、スコープ外とみて矛盾しない。
- 19 件のうち**要旨が無いものが 12 件**(題名だけで落ちた)。
- **この除外はルールどおり。** `rule.md` §(Cat1)は `augmented reality` `ar` `mixed reality` `mr` を
  「AR/MR では実環境が視野に残り、完全な視覚的置換を前提とする自己スケール操作が成立しない」(I 基準)として除外している。
  したがって `6X75UZKY` の除外はルール違反ではなく、**ルール自体の境界例**(多スケールの MR で巨人になる)である。
  前に「再現率の問題」と書いたのは言い過ぎで、設計上の除外が境界例に当たった、が正確。

## 題名にスケール系の語がある 65 件のうち、境界とみられるもの(題名だけの判断。要旨・本文は未確認)

| Key | 年 | 題名 | 落ちた理由 | 論点 |
|---|---|---|---|---|
| 6X75UZKY | 2018 | Superman vs giant: spatial perception for a multi-scale MR flying telepresence interface | Cat1(MR) | 巨人化の知覚。MR(実環境が視野に残る) |
| 3FZLALZG | 2021 | Multi-scale mixed reality collaboration for digital twin | Cat1(MR/AR) | 多スケール。MR |
| KQUQDC4A | 2019 | The influence of size in augmented reality telepresence avatars | Cat1(AR) | アバターのサイズ。AR |
| 4GZ95NX8 | 2026 | Physio avatar RM: self-avatar integration with foot-elongated avatar | Cat3(rehabilitation) | 足を伸ばしたアバター。臨床語で落ちた |
| 7AHG4QVW | 2023 | Embodiment of virtual feet correlates with motor performance in a target-stepping task | Cat3(patients) | 仮想の足。患者語で落ちた |
| WIAKNYXP | 2018 | Changing the size of a mirror-reflected hand does not affect pain perception | Cat3(pain) | 手のサイズ操作。鏡(VR か未確認) |
| MYRX6AUC | 2019 | From avatars to body swapping: VR for assessing and treating body-size distortion | Cat3(patients) | 身体サイズの歪み。臨床 |
| 4YY9QKZS | 2016 | A VR full body illusion improves body image disturbance in anorexia nervosa | Cat3(patients) | 同上 |
| B7JA66EB | 2018 | Body schema distortion in anorexia nervosa | Cat3(CBT) | 同上 |
| C89J5NQI | 2016 | VR body swapping: modifying the allocentric memory of the body | Cat3(patients) | 同上 |
| SGJLADP5 | 2018 | Assessing body image in anorexia nervosa using biometric self-avatars in VR | Cat3(patients) | 同上 |
| QQUBEZAR | 2010 | Body image in eating disorders: exposure to VR environments | Cat3(patients) | 同上 |
| J9FE7KG8 | 2016 | The effects of avatars, stereo vision and display size on reaching | Cat1(desktop)・Cat3 | 表示サイズ。デスクトップ |

- 臨床集団(摂食障害など)の身体サイズ歪みは、Cat3 の意図(臨床・治療目的はスコープ外、Rev.8 の考え方)に沿った除外。
- 4GZ95NX8・7AHG4QVW は、健常者の実験でもキーワード(`rehabilitation`、`patients`)だけで落ちた可能性がある。要旨で要確認。
- `\bar\b` は 50 件に当たっており、AR 以外の語(略語など)を拾っていないかは未確認。

## 未確認・判断が要ること

1. 上表の 13 件を要旨・本文で確認するか(特に 6X75UZKY、3FZLALZG、4GZ95NX8、7AHG4QVW)。
2. 6X75UZKY の扱い: ルール上は Exclude だが、巨人化(自己スケール)を扱う。境界例として Limitations に書くか、
   MR の除外をスケール操作に限り緩めるかは著者の判断(プロトコル変更なら changelog に Rev. で記録)。
3. `screening/` は凍結中。step 3 の再実行はしていない。
4. 題名に scale 系の語が無い論文は見ていない(65 件は題名の正規表現による)。
