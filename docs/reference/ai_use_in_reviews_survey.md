# レビュー論文での AI 使用と、信頼性・再現性の担保(調査メモ)

> 作成: 2026-11-20。2026-11-19 の MTG で出たタスク「AI を使ったサーベイ論文は、信頼性・再現性をどう担保しているか」の途中結果。
> **状態: 暫定。** 網羅できていない(下の「調べ方と限界」)。Phase 4 のテスト計画に何を足すかは、次回 MTG で決める(下の §6)。

## 1. 調べ方と限界

- 対象: 2023〜2026 年に、トップの会議・論文誌(ACM CSUR / TOCHI / TOSEM、CHI・CSCW・UIST ほか、IEEE TVCG・IEEE VR・ISMAR・TSE ほか)に採択されたレビュー論文のうち、**レビュー作業そのもの**(検索・絞り込み・抽出・コーディング・分類)に AI を使ったもの。LLM が題材なだけで、作業は人手のものは対象外。
- 方法: Web 検索(ドメインを dl.acm.org / ieeexplore.ieee.org / arxiv.org に限定、計約 70 クエリ)。方法の節は arXiv 版で確かめた。2026-11-19、Haiku のサブエージェント 3 体で分担。
- **限界:** ACM DL は直接の取得を 403 で拒否し、IEEE Xplore は内容が取れなかった。データベースの全文検索はかけていない。**見つかった件数が少ないのは、実際に少ないからなのか、検索経路の限界なのかを区別できない。** 網羅するなら、ログイン済みのブラウザで ACM DL / IEEE Xplore の全文検索をかける必要がある(Chrome 連携は 2026-11-20 時点で未接続)。
- 生の結果: セッションの一時フォルダにあった `ai_reviews_acm_journals.md` / `ai_reviews_acm_conf.md` / `ai_reviews_ieee.md`(リポジトリには入れていない。要点は本ファイルに転記済み)。

## 2. 見つかった論文

### 確認済み(掲載先と方法)

| 論文 | 掲載先 | AI の使い方 | 信頼性・再現性の担保 |
|---|---|---|---|
| Kostikova et al., *LLLMs: A Data-Driven Survey of Evolving Research on Limitations of Large Language Models* | ACM CSUR(2026、DOI 10.1145/3801096。掲載先は検索の要約と arXiv の脚注で確認、DL のページは未確認) | 約 25 万件を分野の語で絞ったあと、LLM が要旨を 0〜5 で評価し、根拠の箇所も抜き出す(14,648 件を残す)。クラスタの命名に GPT-4o | 人 4 名で作った正解セット 445 件(人同士の重み付き κ 0.75)と比べ、Llama-3.1-70b は κ 0.74 / 根拠の F1 0.65。GPT-4o(gpt-4o-2024-08-06)・Mistral-7B・SBERT+ロジスティック回帰と比べて選定。クラスタは 110 件を人が再アノテーション。モデルの版・量子化を明記し、データと手順を GitHub で公開 |
| Pang et al., *Understanding the LLM-ification of CHI* | CHI 2025(DOI 10.1145/3706598.3713726) | 予備段階で gpt-4o-2024-05-13 にトピックを探らせたが、テーマが一般的すぎて使えなかった。**本番のコーディングは人手** | LLM を使わないこと自体が担保。理由は「適切な開示と評価なしに LLM を使うことへの懸念」。人のコードと書誌を GitHub で公開 |
| Scherbakov et al., *The emergence of large language models as tools in literature reviews: a LLM-assisted systematic review* | JAMIA 2025(DOI 10.1093/jamia/ocaf063。医療情報学) | Covidence の拡張機能から GPT-4o で、要旨の判定・全文の判定・データ抽出 | 3 回実行して多数決。人 2 名で基準を校正してから、各段 3 つのプロンプトを試作。人の合意(要旨 100 件・全文 30 件)と照合。抽出は精度 80% 未満の項目だけ人が見直す。OSF に事前登録、プロンプトは補足資料。**温度の記載なし、人と LLM の κ なし**。数値の抽出は精度が低いと著者自身が認めている |

### 掲載先がトップではない、または未確認(参考)

| 論文 | 掲載先 | 要点 |
|---|---|---|
| Besançon & Isenberg(IEEE VIS 論文の倫理承認の記載) | arXiv 2608.13295(採択先未確認) | 人手でコーディングした後に LLM で照合。不一致は読み直し、LLM の出力とスクリプトを公開 |
| *Mapping the Challenges of HCI: … ChatGPT for Mining Insights at Scale* | IJHCI 2026 | CHI 2023 の 879 本から GPT-3.5 で抽出、GPT-4 で順位づけ。人の評価で κ 0.97。版・温度・プロンプトの記載なし |
| *Show Your Title!*(SE の発話研究のスコーピングレビュー) | QUATIC 2025 | 9,000 件超の題名を GPT で判定。人との不一致 13%。κ・版・正解セットの規模の記載なし |
| *Visualizing 30 Years of CHI Research with Generative AI* | DOI 10.1145/3772363.3798338(掲載先・方法とも未確認) | CHI の要旨 11,847 件を LLM でコーディング。ブートストラップと感度分析をしたとあるが、人との比較は不明 |
| AIDME(AI 支援のスコーピングレビュー) | DOI 10.1145/3731120.3744586(未確認) | LLM が基準を当てて事前に絞り込み、人が監督 |
| *Charting the Growth of Social-Physical HRI* | ACM HRI(DOI 10.1145/3776734.3794506、方法は未確認) | 小型の言語モデルで要旨を判定 |
| *Towards Automating Articles Screening Processes Using CoT LLMs* | DOI 10.1145/3774905.3795601(未確認) | — |
| XR のヘルスケア・ウェルビーイング(IEEE VR / ISMAR 2020–2025 のレビュー) | ieeexplore 11236117(未確認) | AI を使ったかどうか不明 |
| Kostikova 以外の CSUR / TOSEM の LLM サーベイ(LLM for Algorithm Design、LLM for CAD、LLM4SE ほか) | CSUR / TOSEM | **題材は LLM だが、絞り込みと抽出は人手** |

### ガイドライン

- **RAISE**(Responsible AI in Evidence Synthesis、v2 は 2025-06)と、Cochrane・Campbell・JBI・CEE の共同声明(2025): 判定を行う、または提案する AI の使用は、すべて報告する。
- **PRISMA-trAIce**(Holst et al., JMIR AI 2025): レビューで AI を使ったときの報告項目。PRISMA 2020 の拡張案(正式な拡張ではない)。
- Research Synthesis Methods の投稿ガイダンス(2025-12): AI の出力をどう検証したかの記載を求める。

## 3. 使い方の分類

| 型 | AI がやること | 人がやること | 例 |
|---|---|---|---|
| **A. 使わない** | なし(探索的に試すだけ) | すべて | Pang CHI'25 |
| **B. 人の後に照合だけ** | 人の結果との突き合わせ | 判定・コーディングはすべて人。不一致は人が読み直す | Besançon & Isenberg |
| **C. 人の代わりに一部を判定** | 判定、値の抽出 | 少数の正解セットで精度を確かめ、精度の低い項目だけ直す | Scherbakov JAMIA'25 |
| **D. 大量の文献を自動で分類** | 数万件の分類・クラスタリング | 正解セットを作り、分類の妥当性を確かめる | Kostikova CSUR'26 |

規模ではっきり分かれる。
- **数百件規模**の体系的レビュー(HCI の主流)は A か B。
- **数万件規模**の計量的なサーベイは D。人手では無理だから使う、という正当化。
- C は医療情報学で見つかったもので、HCI・VR のトップ会議では確認できなかった。

## 4. 担保の方法

| 担保の方法 | A | B | C | D |
|---|---|---|---|---|
| 人の正解セットと比べる(κ・精度) | – | ○(不一致の件数) | ○(要旨 100 / 全文 30) | ◎(445 件、人同士の κ を基準に) |
| 複数回実行・複数モデルの比較 | – | – | ○(3 回、多数決) | ◎(4 モデルを比べて選定) |
| 人が見直す範囲 | すべて | 不一致 | 精度 80% 未満の項目 | 抽出した標本 |
| モデルの版の明記 | ○ | ? | ○ | ◎(版名・量子化まで) |
| プロンプト・出力の公開 | – | ○ | △(補足資料) | ◎(GitHub) |
| 事前登録 | – | – | ○(OSF) | – |
| 温度などの設定 | – | ? | ×(記載なし) | △ |

**共通点: 「同じ出力が出ること」としての再現性はあきらめている。** 代わりに、(1) 人の基準と比べた妥当性(κ・精度)と、(2) 出力を公開して第三者が検証できること、で担保している。RAISE・共同声明・PRISMA-trAIce の方向とも一致する。

**弱いところ(査読で突かれやすい):**
- 正解セットが小さい(要旨 100 / 全文 30)
- 人と AI の κ を出していない(精度だけ)
- 温度・シードを書いていない
- 数値の抽出の精度が低い(JAMIA の著者自身が認めている。本サーベイのテストでも、LLM が数字を写し間違えた例がある)

## 5. 本サーベイ(Rev.31)との比較

本サーベイは **B と C の中間で、上の例のどれよりも人の判断に残す範囲が広い**。

| 観点 | 本サーベイ(Rev.31) | 既存のレビューとの違い |
|---|---|---|
| AI の役割 | 該当箇所の引用と頁だけ。判定も値も書かせない | C・D より狭い。B に近い |
| 担保の方法 | 引用が全文にあるかを文字列で照合する(33 件 × 3 回のテストで 99.4% が一致) | 正解セットとの統計的な比較ではなく、**出力を一件ずつ決定論的に検証できる**。上の例のどれも採っていない。**新しさとして主張できる** |
| 複数回の実行 | 3 回実行して**和集合**を担当者に見せる(見落としを減らす目的) | C の多数決とは逆の発想。理由(1 回では見落とす。3 回の完全一致 22%、重なり 91%)を書く必要がある |
| 公開 | モデル ID・実行日・プロンプトの版・出力を公開 | D と同水準 |

**足りないもの(§6 で MTG 判断):**
1. 人だけで抽出した結果との比較がない。抜き出しが人の見落としを減らしたのか、増やしたのかを示す数字がない。
2. 温度・シードの記録。
3. PRISMA-trAIce の項目との照合。

## 6. 次回 MTG で決めること

- [ ] 上の 1〜3 を Phase 4 のテスト計画に入れるか(入れるなら、1 は 33 件のテストの一部を人だけでも抽出して比べる)
- [ ] 網羅的な調査を続けるか(続けるなら、ACM DL / IEEE Xplore の全文検索をブラウザで行う)

## 7. 原稿での位置づけ(案。原稿の改稿は承認ゲートの対象)

- 方法の節で「既存のレビューは LLM の判定を人の基準と統計的に比べて正当化している[Scherbakov JAMIA'25; Kostikova CSUR'26]。本研究は LLM に判定させず、出力を原文との文字列照合で決定論的に検証できる形に限定した」と位置づける。根拠として RAISE(共同声明)と PRISMA-trAIce を引く。
- `main.tex` L252–254・L542–551 の「every automated step is deterministic」は、この位置づけで書き換えられる。

## 出典

- Pang et al. CHI 2025: https://arxiv.org/abs/2501.12557
- Scherbakov et al. JAMIA 2025: https://academic.oup.com/jamia/article/32/6/1071/8126534
- Kostikova et al. (LLLMs): https://arxiv.org/abs/2505.19240
- Besançon & Isenberg: https://arxiv.org/abs/2608.13295
- Mapping the Challenges of HCI: https://arxiv.org/abs/2306.05036
- Show Your Title!: https://arxiv.org/abs/2510.12294
- Cochrane ほか共同声明(RAISE): https://pmc.ncbi.nlm.nih.gov/articles/PMC12603384/
- PRISMA-trAIce: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12694947/
- Research Synthesis Methods の投稿ガイダンス: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12873612/
- Mäntylä et al.(SE のスクリーニングでの LLM と人の不一致): https://arxiv.org/abs/2606.17588
