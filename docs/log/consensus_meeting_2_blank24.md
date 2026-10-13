# 協議ミーティング2: 最終判定が空欄の 24 件

作成日: 2026-10-13
元データ: `consensus_meeting_2.xlsx`(OneDrive。デスクトップ版 2026-10-13 11:19 更新)の「協議」シート。
このファイルは git 未追跡のまま、別デバイスで編集されたもの。

## 全体像

- 協議対象: 183 件(校正セット 223 件のうち、不一致または Unsure)
- 最終判定の記入済み: 159 件(Exclude 141 / Include 18)
- 最終判定が空欄: **24 件**(本書の対象)
- 協議ルール: 結論が出ない場合は **Include に倒す**(誤 Exclude は回復不能、誤 Include は Phase 4 の手間が増えるだけ)

## 空欄 24 件の特徴

- 全件が「著者 Unsure ＋ もう1名が Exclude(または Unsure)」の形。**2名以上が Exclude の件はない**。
- 3人目の判定欄が空の行が大半。Kataoka・Watanabe の空欄の扱い(判定を待つか、協議で決めるか)を先に決める必要がある。
- 協議メモの記入があるのは 7 件(#17, #18, #19, #20, #21, #23, #24)。

判定の略記: U = Unsure、E = Exclude。括弧内は除外理由。

## A. 著者 Unsure ＋ Watanabe Exclude(Kataoka 未判定) 14 件

| # | ID | 論文 | 判定 | 論点 |
|---|---|---|---|---|
| 1 | R0a68d4435 | Large errors, but no depth compression, in walked indications of exocentric extent(Perception & Psychophysics) | 著 U / W E(スコープ外) | |
| 2 | R0ae21cf3e | Can Virtual Human Entourage Elements Facilitate Accurate Distance Judgments in VR?(EuroVR) | 著 U / W E(スコープ外) | 距離知覚は軸の候補 |
| 3 | R12624d2c7 | Effects of virtual environments and self-representations on redirected jumping(VRW 2021) | 著 U / W E(I) | 自己表現(アバター)の効果 |
| 4 | R1907f1152 | On temporal-spatial realism in the virtual reality environment(UIST '91) | 著 U / W E(スコープ外) | |
| 5 | R272b2107d | Visual guidance of walking through apertures: body-scaled information for affordances(JEP:HPP) | 著 U / W E(スコープ外) | body-scaled affordance。VR ではない可能性 |
| 6 | R4525cca6b | Asymmetric normalization in social virtual reality studies(VRW 2022) | 著 U / W E(I: HMD-VR でない) | |
| 7 | R648c5a9fd | New Virtual Reality for Architectural Investigations(eCAADe) | 著 U / W E(スコープ外) | |
| 8 | R6a9ba9fa3 | Distance: a framework for improving spatial cognition within digital architectural models(掲載先なし) | 著 U / W E(スコープ外) | |
| 12 | R900bf8c85 | Human and machine: Evaluating whether action automation influences visual perception(AP&P) | 著 U / W E(スコープ外) | |
| 15 | Ra4db28b47 | Exploring proprioception and spatial awareness during auditory and visual feet guidance in bouldering(VRW 2026) | 著 U / W E(I) | |
| 17 | Rc2efa32b5 | Beaming into the Rat World(PLoS ONE) | 著 U / W E(P) | メモ: 人間だけの実験がありそう |
| 20 | Rd716a5d10 | Can you help me concentrate room?(VR 2010) | 著 U / W E(I: HMD-VR でない) | メモ: 本文に「we use virtual reality」の記載あり |
| 21 | Rdc8e0d552 | "Did she just tap me?": multisensory feedback for social touch(Front. VR) | 著 U / W E(I) | メモ: 協議予定 |
| 22 | Rf568c011a | Perceptual thresholds of visual size discrimination in augmented and virtual reality(Computers & Graphics) | 著 U / W E(スコープ外) | **サイズ知覚そのもの。スコープ内の可能性が高い** |

## B. 著者 Unsure ＋ Kataoka Exclude(Watanabe 未判定) 7 件

| # | ID | 論文 | 判定 | 論点 |
|---|---|---|---|---|
| 9 | R746b5156f | Gibson 1979, The ecological approach to visual perception(書籍引用の断片) | 著 U / K E(I) | 論文ではなく文献リストの断片。**同定が必要** |
| 11 | R8d07df5d9 | Real-time dynamic digital twin generation using multiple first-person views(VRW 2026) | 著 U / K E(I) | |
| 13 | R90145a337 | Perception of Characters in VR: How a character's height affects the perception(掲載先なし) | 著 U / K E(I) | 他者(キャラクター)のスケール |
| 14 | Ra3f61e703 | Peri-personal space as a prior in coupling visual and proprioceptive signals(Sci Rep) | 著 U / K E(I) | |
| 16 | Rbd45fc72f | 「Proc. IEEE Virtual Reality, 275--276」 | 著 U / K E(スコープ外) | **タイトルが出典情報で、論文を特定できない** |
| 18 | Rc715a1e3f | Short term motor-skill acquisition improves with size of self-controlled virtual hands(PLoS ONE) | 著 U / K E(I: HMD-VR でない) | メモ: 「3D Virtual Reality devices」が HMD かが論点 |
| 23 | Rfb4b73910 | Inner child: The role of VR child avatars in improving adult language learning(ISMAR-adj 2024) | 著 U / K E(I) | メモ: 子供になる＝スケール操作? |

## C. 著者 Exclude ＋ Kataoka Unsure(Watanabe 未判定) 2 件

| # | ID | 論文 | 判定 | 論点 |
|---|---|---|---|---|
| 10 | R7cf672a5d | Virtual object sizes for efficient and convenient mid-air manipulation(The Visual Computer) | 著 E(O) / K U | メモ: HMD とは言っていないが、色々なサイズの仮想物体の操作性を評価していそう |
| 19 | Rd3085f2d6 | Navigation modes, operation methods, observation scales and background options in UI design(JCDE) | 著 E(O) / K U | メモ: スケールはしてそう。協議予定 |

## D. 著者 Unsure ＋ Kataoka Unsure(Watanabe 未判定) 1 件

| # | ID | 論文 | 判定 | 論点 |
|---|---|---|---|---|
| 24 | Rcfe9667f4 | 「H5 - Users who spend more time in Giant mode will show a stronger under-estimation effect」 | 著 U / K U | メモ: 協議予定。自分が巨人になって何かを評価していそう。**タイトルが仮説文で論文名が不明** |

## 優先して議論したい件

1. **#22(視覚サイズ弁別閾値)** と **#24(Giant mode)** はスコープ内の可能性が高い。
2. **#9 / #16 / #24** はタイトルや出典が壊れていて、論文を特定できない。DOI や `ResearchVR4.csv` との照合で同定してから判定する。
3. **#10 / #18 / #19** は、HMD の有無とスケール操作の有無を全文で確認する対象。

## 未確認事項

- 記入済み 159 件の最終判定を誰がいつ入れたか(会議で追認するだけか、見直すのか)。
- Kataoka・Watanabe の判定が空欄の行が、全 183 件中それぞれ 56 件・50 件ある。校正セットは3名全員が判定する設計のため、未回収かどうか確認が要る。κ にも影響する。
- `consensus_meeting_2.xlsx` は git 未追跡。`screening/consensus/` への配置は指示待ち。
