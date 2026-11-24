# 体形の変化(太る・痩せる)を対象に含めるか(分析メモ)

> 作成: 2026-11-20。2026-11-19 の MTG で出たタスク「体形を変化させるタイプは、スケール感 = 身長感覚に関係ないとして弾いてきたが、サーベイの貢献を考えるなら入れるべきでは。今のプロトコルの解釈としてどうすれば入れられるか、具体的な方法はあるか」への回答。
> **2026-11-21: 方針が決まり、`protocol_changelog.md` Rev.33 として記録した**(§3 の規則の案を採用。§5 のうち「操作なしで推定だけ」の型と筋肉量の変化は未決)。以下は当時の分析。
> **状態(作成時): 分析のみ。** `rule.md`・`phase4_reviewer_guide.md`・判定シートは変えていない(Phase 3b・Phase 4 のシートは凍結中、プロトコルの変更は MTG で決める)。
> 再現: `python -X utf8 scripts/trace_body_shape.py outputs/body_shape_trace.csv`(SurveyProtocol/ で実行)。

## 1. 結論

- **今の文言のままで入れられる。** I_scale は「身体・身体部位・アバターの**サイズ**を操作」で、身長に限るとはどこにも書いていない。「スケール = 身長」は評価者の読み方で、プロトコルの文言ではない。
- **体形系の論文は、まだ全部は弾かれていない。** 14 件が Phase 4 に残っていて、協議待ち(`screening/phase4/consensus_worklist.csv`)。3 人の判定が割れているので、**いま規則をはっきりさせれば手戻りが最小**。
- やり直しが要るのは人の判定の段(Phase 3b と Phase 4)だけ。機械的な段(P1〜P3a)は I の解釈に依存しないので、やり直し不要。
- 検索式そのものに穴がある(第 3 群に weight / shape / width が無い)。ここは引用の追跡で回収し、限界として書く。

## 2. どの段で落ちていたか

重複削除後の 18,342 件(`data/pipeline/step1_dedup.csv`)のうち、題名か要旨に体形の語(body weight / overweight / obese / fat / thin / slim / body shape / body image / belly / waist / BMI / eating disorder ほか。正規表現は `scripts/trace_body_shape.py` の `SHAPE`)を含む **696 件**を追った。

| 段 | 件数 | 落ちた理由 | 解釈の変更で結果が変わるか |
|---|---|---|---|
| P1.5 フィルタ層 | 372 | 3 概念群の語がそろわない | 変わらない(機械的) |
| P2 掲載先 | 170 | 掲載先のランク | 変わらない(機械的) |
| P3a キーワード除外 | 79 | ほぼ Cat3(臨床。摂食障害・疼痛・リハビリの患者) | 変わらない(P 基準による除外で、I とは無関係) |
| P3b 要旨の判定で Exclude | 61 | 大半は無関係(布のシミュレーション、医学、運動処方など)。**数件が「I: スケール操作なし」で外れている** | **変わる** |
| **Phase 4 に残っている** | **14** | 協議待ち | **変わる** |

語の一致で拾っているので、696 件の大半は主題が無関係(例: 「thin」を含む触覚デバイスの論文)。数字は「語を含む記録の行き先」で、体形研究の件数ではない。

### P3b で「スケール操作なし」として外れた、主題が近いもの

| record_id | 論文 | 第 2 評価者の理由・メモ |
|---|---|---|
| `R9b217661f` | Impact of an overweight body representation in virtual reality on locomotion in a motor imagery task(Psychological Research 2023) | Kataoka「I: スケール操作なし」、メモ「**迷ったが過体重であり,スケールとは違うと判断**」 |
| `R0877910b9` | Shaping health behaviors beyond reality: A full body illusion to experience the consequences of obesity(CHB 2024) | 「O: スケール知覚の測定なし」 |
| `Rd70fe1d6d` | Body image and anti-fat attitudes: … haptic virtual reality(CyberPsych 2016) | Kataoka「I: スケール操作なし」、メモ「肥満とかの話」 |
| `Rf79bb8988` | Body image avoidance affects interpersonal distance perception(EEDR 2020) | Kataoka「I: スケール操作なし」 |
| `R70f315a56` | Developing a novel measure of body satisfaction using virtual reality(PLoS ONE 2015) | Watanabe「I: スケール操作なし」 |
| `R51cabd000` | The threat of an embodied virtual belly affects gastric feelings(Sci Rep 2025) | Kataoka「I: スケール操作なし」 |
| `Rc41cf0d9e` | Exercise in VR with a muscular avatar influences performance on a weightlifting exercise(Cyberpsychology 2021) | 「スコープ外」 |

※ 著者の stage 1 の判定はリポジトリ内の `sheet_author.xlsx` が空欄のため確認できていない(記入済みの版は別の場所にある)。

### Phase 4 に残っている 14 件と、現在の I_scale の判定

| record_id | 論文(略) | 著者 | 相手 | 相手のメモ |
|---|---|---|---|---|
| `R581775bb4` | Owning an overweight or underweight body(Piryankova 2014) | Y | Kataoka ? | 「**体格を変える系はスケール操作と見做すか議論しておいた方がいいかも**」 |
| `R995d82790` | Illusion of larger belly size(Normand 2011) | Y | Kataoka ? | 「アバターの体格の取り扱いは要議論」 |
| `R9244e981d` | Emotions toward an overweight avatar | Y | Kataoka ? | 「アバターの体格の取り扱いは要議論」 |
| `Re06bf4a0e` | Avatar appearance (normal vs obese) and locomotion | Y | Kataoka ? | 「アバターの体格の取り扱いは要議論」 |
| `R36d0a0077` | Illusory changes in body size modulate body satisfaction(Preston 2014) | Y | Watanabe Y | |
| `R3dfe61f94` | Visually manipulating back size and morphology | Y | Kataoka Y | |
| `R0340e93be` | Visuo-tactile congruency … (more corpulent body) | Y | Watanabe Y | |
| `R2bc2509b2` | Gender differences in bodily experience | Y | Watanabe N | 体形は操作せず、視触覚刺激で身体サイズの推定を測る |
| `R526151b55` | Playing with Spatial Frames | Y | Kataoka N | 「仮想の身体は標準の体格」 |
| `Rd7aadd900` | Proteus effect: avatar muscularity and pain | ? | Watanabe Y | |
| `R61cafb0ec` | Towards an altered body image(体重 ±20%) | Y | Watanabe Y | 著者は S(抄録のみ)で Exclude |
| `R9865af17c` | Does distance matter? Personalized avatars | —(担当外) | Kataoka ? | ペアは Kataoka×Watanabe。協議待ちリストに I_scale = ? で載っている |
| `Rf838e7bc8` | Estimating avatar weight from footstep sounds | —(担当外) | Kataoka Y / Watanabe Y | 両者 Include 済み |
| `R52ad50380` | Waist-mounted interface for viewpoint height | Y(Unsure) | Watanabe Y | 体形ではなく視点の高さ(語の一致で拾っただけ)。著者の Unsure は MR の扱い |

評価者によって読み方が違う(著者はほぼ Y、Kataoka は ? か N、Watanabe は混在)。

## 3. 入れるための解釈

`phase4_reviewer_guide.md` §3 の I_scale は「身体・身体部位・アバターの**サイズ**、視点の高さ、IPD、環境や物体のスケールを**操作**」。体の幅・周径の変化は「身体のサイズの操作」に含まれる、と読める。根拠は次のとおり。

1. **自分の身体を「ものさし」にする考え方では、ものさしは身長だけではない。** 眼高のほかに、肩幅(隙間を通れるかの判断。Warren & Whang 1987)や手の大きさも使う。体の幅が変われば、世界との寸法の関係(アフォーダンス)が変わる。Piryankova 2014 は実際にアフォーダンスの推定と身体サイズの推定を測っている。
2. **O 基準の「主観的サイズ推定・アフォーダンス判断」に、そのまま当てはまる。**
3. **既存の判断と整合する。** 「足音からアバターの体重を推定」(`Rf838e7bc8`)は 2 人とも Include。参考文献予定に Tajadura-Jiménez 2015(体重の知覚)、Normand 2011 がある。

### 判定規則の案

> レンダリングされた**自己**身体の寸法(長さ・幅・周径)のどれかが変わる操作は、I_scale = Y。全身が一様に拡大・縮小するものに限らず、方向によって倍率が違う変化(体形の変化)も含む。

N のままにするもの:
- 他人のアバターの体形を見るだけ(自己の寸法が変わらない)
- 寸法が変わらない外見の変更(肌の色・性別・年齢・服装)
- 操作がなく、身体満足度などを質問紙で測るだけ
- 操作はなく、身体サイズの推定だけを測るもの(`R2bc2509b2` `R526151b55` のような型)は、多感覚刺激が「身体サイズの知覚に関わるように設計」されていれば、今の規則で Y になりうる。MTG で確認する。

筋肉量の変化(`Rd7aadd900` `Rc41cf0d9e`)は、幅が変わるので規則上は Y。ただし主題が痛み・運動成績で、O(スケールの変化を測る定量データ)で落ちる可能性がある。

この規則は、軸 1 の下位区分の案(PROGRESS_LOG の Rev.26 の宿題: 「レンダリングされた身体形状が変わったか」を第一の判定にする。全身 → Global、部位 → Local)とも整合する。

## 4. 具体的な手順(案)

1. **規則を決めて記録する。** `protocol_changelog.md` に Rev.33 として、判定をやり直す前の日付で書く。Phase 3b は 2026-08-19 に凍結済みなので、「I 基準の**明確化**」として記録し、**逸脱**として限界の節(Threats to Validity)で報告する。
2. **P1〜P3a はやり直さない。** 機械的な基準で、I の解釈に依存しない(上の表)。
3. **P3b の再判定。** P3b で Exclude にした記録のうち、体形の語(語のリストを事前に固定する。`trace_body_shape.py` の `SHAPE`)を含む 61 件を、新しい規則で要旨を再判定する。方式は Phase 3b と同じ 2 段(著者が全件 → 著者の Exclude / Unsure を第 2 評価者が確認。1 人が Include なら通す)。校正セット(κ)は設けない(2026-11-24 に決定。`screening/rescreen_bodyshape/README.md`)。通ったものは Phase 4 へ。
4. **Phase 4 の 14 件**は、今回の協議で新しい規則を当てはめて決着させる。
5. **検索の段の穴。** 検索式の第 3 群(Size / Scale / Height / Distance)に weight / shape / width が無い。たとえば Tajadura-Jiménez et al., *As Light as Your Footsteps*(CHI 2015、体重の知覚)は、**重複削除後のデータに一度も現れない**(検索に掛かっていない)。検索のやり直しはせず、引用の追跡(`snowballing_protocol.md`)で回収し、限界として明記するのが現実的。

## 5. MTG で決めること

- [ ] 体形の変化を I_scale = Y とするか(§3 の規則の案)
- [ ] N のままにするものの範囲(とくに「操作なしで身体サイズの推定だけ」の型と、筋肉量の変化)
- [ ] P3b の 61 件の再判定を誰がやるか
- [ ] 分類(軸 1)で、体形の変化をどの区分に入れるか(Global / Local。必要なら抽出列 `scale_target` に値を足す)

## 関連

- 追跡の全リスト: `outputs/body_shape_trace.csv`(696 件。列: Key, rid, year, title, venue, terms, stage)
- 追跡のスクリプト: `scripts/trace_body_shape.py`
- Phase 4 の協議待ちリスト: `screening/phase4/consensus_worklist.csv`
- I_scale の現行の運用: `docs/reference/phase4_reviewer_guide.md` §3
