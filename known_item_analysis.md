# Known-Item 脱落分析レポート

> `scripts/known_item_test.py` による自動生成(2026-08-11)。
> Known-Item 12 件。判定は全て決定論的(DOI/正規化タイトル一致)。
> FUZZY 候補は手動確認が必要であり、recall には算入していない。

## 段階別 recall

| 段階 | 内容 | 生存 | recall |
|---|---|---|---|
| step0 | 統合生データ(検索式で拾えたか) | 8/12 | 66.7% |
| step1 | 重複削除後 | 8/12 | 66.7% |
| step2 | Venueランク通過後 | 3/12 | 25.0% |
| step3 | キーワード除外通過後(最終候補) | 3/12 | 25.0% |

## step0 脱落 — 検索式の欠陥

### Being Barbie: The Size of One's Own Body Determines the Perceived Size of the World

- DOI: `10.1371/journal.pone.0020195` / 想定Venue: PLoS ONE 6(5) e20195
- タイトルに対する検索クエリ・コンセプト群の命中状況:
  - G2 身体表象: ✅ `\bbod(?:y|ies)\b`
  - G3 スケール知覚: ✅ `\bsizes?\b`
  - G1 没入環境: ❌ 命中なし ← **検索式が取りこぼす原因(の候補)**
- タイトル中の内容語(キーワード追加候補の母集団): `being`, `barbie`, `size`, `one`, `own`, `body`, `determines`, `perceived`, `size`, `world`
- 提案: 上記 ❌ のコンセプト群に、この論文で使われている同義語を OR 追加して再検索し、ヒット件数の増分を確認する。
- 注: 実際の検索は Title+Abstract 対象のため、Abstract に命中語がある可能性もある。原文 Abstract を確認のうえ判断すること。

### The effects of eye height and self-avatars on distance estimation in virtual reality: A replication study

- DOI: `10.3389/frvir.2020.588701` / 想定Venue: Frontiers in Virtual Reality 1:588701
- タイトルに対する検索クエリ・コンセプト群の命中状況:
  - G1 没入環境: ✅ `\bvirtual reality\b`
  - G2 身体表象: ✅ `\bavatar[s]?\b`
  - G3 スケール知覚: ✅ `\bheights?\b`, `\bdistances?\b`
- タイトル中の内容語(キーワード追加候補の母集団): `eye`, `height`, `self-avatars`, `distance`, `estimation`, `virtual`, `reality`, `replication`
- 提案: 上記 ❌ のコンセプト群に、この論文で使われている同義語を OR 追加して再検索し、ヒット件数の増分を確認する。
- 注: 実際の検索は Title+Abstract 対象のため、Abstract に命中語がある可能性もある。原文 Abstract を確認のうえ判断すること。

### The Plausibility Paradox for Resized Users in Virtual Environments

- DOI: `10.3389/frvir.2021.655744` / 想定Venue: Frontiers in Virtual Reality 2:655744
- タイトルに対する検索クエリ・コンセプト群の命中状況:
  - G1 没入環境: ❌ 命中なし ← **検索式が取りこぼす原因(の候補)**
  - G2 身体表象: ❌ 命中なし ← **検索式が取りこぼす原因(の候補)**
  - G3 スケール知覚: ❌ 命中なし ← **検索式が取りこぼす原因(の候補)**
- タイトル中の内容語(キーワード追加候補の母集団): `plausibility`, `paradox`, `resized`, `users`, `virtual`, `environments`
- 提案: 上記 ❌ のコンセプト群に、この論文で使われている同義語を OR 追加して再検索し、ヒット件数の増分を確認する。
- 注: 実際の検索は Title+Abstract 対象のため、Abstract に命中語がある可能性もある。原文 Abstract を確認のうえ判断すること。

### Enhancing Virtual Walking Sensation Using Self-Avatar in First-Person Perspective and Foot Vibrations

- DOI: `10.3389/frvir.2021.654088` / 想定Venue: Frontiers in Virtual Reality 2:654088
- タイトルに対する検索クエリ・コンセプト群の命中状況:
  - G2 身体表象: ✅ `\bavatar[s]?\b`
  - G1 没入環境: ❌ 命中なし ← **検索式が取りこぼす原因(の候補)**
  - G3 スケール知覚: ❌ 命中なし ← **検索式が取りこぼす原因(の候補)**
- タイトル中の内容語(キーワード追加候補の母集団): `enhancing`, `virtual`, `walking`, `sensation`, `self-avatar`, `first-person`, `perspective`, `foot`, `vibrations`
- 提案: 上記 ❌ のコンセプト群に、この論文で使われている同義語を OR 追加して再検索し、ヒット件数の増分を確認する。
- 注: 実際の検索は Title+Abstract 対象のため、Abstract に命中語がある可能性もある。原文 Abstract を確認のうえ判断すること。

## step2 脱落 — Venue ホワイトリストの欠陥

### Distortion in Perceived Size and Body-Based Scaling in Virtual Environments

- 脱落理由: Venue名 'ACM International Conference Proceeding Series' が CORE/SJR いずれにも未照合
- ランキングリスト内に類似Venueなし(CORE lev≥0.75 / SJR lev≥0.85 の範囲で候補ゼロ)。`outputs/unmatched_venues_top50.csv` も参照。
- 注記: ランク不足ではなく**照合漏れ**。類似Venueが提示されている場合は表記ゆれであり、正規化ルールまたはエイリアス表への追加で救済可能。類似Venueなしの場合は当該Venueがランキングリスト自体に未収載(ワークショップ等)であり、除外維持が妥当かを個別判断する。

### The influence of eye height and avatars on egocentric distance estimates in immersive virtual environments

- 脱落理由: Venue名 'Proceedings - APGV 2011: ACM SIGGRAPH Symposium on Applied Perception in Graphics and Visualization' が CORE/SJR いずれにも未照合
- ランキングリスト内に類似Venueなし(CORE lev≥0.75 / SJR lev≥0.85 の範囲で候補ゼロ)。`outputs/unmatched_venues_top50.csv` も参照。
- 注記: ランク不足ではなく**照合漏れ**。類似Venueが提示されている場合は表記ゆれであり、正規化ルールまたはエイリアス表への追加で救済可能。類似Venueなしの場合は当該Venueがランキングリスト自体に未収載(ワークショップ等)であり、除外維持が妥当かを個別判断する。

### Dwarf or Giant: The Influence of Interpupillary Distance and Eye Height on Size Perception in Virtual Environments

- 脱落理由: CORE Rank 'C' (< A) のため除外 (venue: 'International Conference on Artificial Reality and Telexistence and Eurographics Symposium on Virtual Environments, ICAT-EGVE 2017' → 照合先: 'International Conference on Artificial Reality and Telexistance & Eurographics Symposium on Virtual Environments')
- ランキングリスト内に類似Venueなし(CORE lev≥0.75 / SJR lev≥0.85 の範囲で候補ゼロ)。`outputs/unmatched_venues_top50.csv` も参照。

### Does Scaling Player Size Skew One's Ability to Correctly Evaluate Object Sizes in a Virtual Environment?

- 脱落理由: Venue名 'Proceedings - MIG 2020: 13th ACM SIGGRAPH Conference on Motion, Interaction, and Games' が CORE/SJR いずれにも未照合
- ランキングリスト内の最近傍(表記ゆれ調査):
  - `ACM SIGGRAPH conference on Motion Interaction and Games` [CORE C] (lev=1.000)
- 注記: ランク不足ではなく**照合漏れ**。類似Venueが提示されている場合は表記ゆれであり、正規化ルールまたはエイリアス表への追加で救済可能。類似Venueなしの場合は当該Venueがランキングリスト自体に未収載(ワークショップ等)であり、除外維持が妥当かを個別判断する。

### Gulliver's virtual travels: active embodiment in extreme body sizes for modulating our body representations

- 脱落理由: SJR 'Q2' のため除外 (venue: 'Cognitive Processing' → 照合先: 'Cognitive Processing')
- ランキングリスト内に類似Venueなし(CORE lev≥0.75 / SJR lev≥0.85 の範囲で候補ゼロ)。`outputs/unmatched_venues_top50.csv` も参照。
- 注記: SJR Q2 による除外。採用基準は「Q1のみ」で確定済み(protocol_changelog.md Rev.4)であり、この脱落は**基準どおりの動作**。 Threats to Validity 節で報告する事例として記録する。

## step3 脱落 — 除外キーワードの誤爆

該当なし。
---

*本レポートは known_items.md 更新のたびに再生成される。手動の解釈・決定は PROGRESS_LOG.md に記録すること。*
