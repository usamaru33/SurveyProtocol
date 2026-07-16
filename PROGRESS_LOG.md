# サーベイ進捗ログ — VR自己スケール知覚 システマティック・レビュー

> このファイルは作業再開時に「今どこまで終わっているか」を思い出すためのログ。
> 作業セッションごとに末尾へ追記していく。プロトコル本文は `rule.md`、実装詳細は `README.md` を参照。

---

## プロジェクトの骨子（30秒で思い出す用）

- **テーマ:** VR空間における自己スケール感覚（Self-scale perception）の形成要因の体系化。
  「視覚情報の支配的影響」と「非視覚的情報（聴覚・触覚）の構造的欠落」を定量的に示すのが狙い。
- **手法:** PRISMA 2020 準拠のシステマティック・レビュー。
- **RQ:** ①検討されてきた感覚モダリティの定量把握 ②介入(IV)と評価指標(DV)の構造的乖離
  ③視覚単独操作の知覚的限界（ミニチュア効果等） ④MLEモデルに基づく多感覚統合の理論的考察
- **分類3軸:** 介入モダリティ（Uni/Multi 2-way/3-way+）× 評価志向（Self/World/Ambiguous）× 知覚支配（Stimulus-Overriding / Context-Dominant / Conflict-Threshold）

---

## タイムライン

| 日付 | 出来事 |
|---|---|
| 2026-05-19 | リポジトリ作成・初回コミット（プロトコル文書、生データ、パイプライン一式） |
| 2026-05-25 | README.md 作成（パイプライン実装ドキュメント）。Phase 1〜3 実行済み・結果確定 |
| 2026-05-25以降 | `year_distribution.py` / `year_distribution.png` 追加（未コミット） |
| 2026-05-27 | 別プロジェクト `../docs-system`（Next.js 文献ブラウザ）を作業 |
| 2026-07-16 | 約1.5ヶ月ぶりに再開。本ログと Claude Code skills を整備 |

---

## 完了していること

### 1. 検索・データ収集
- ACM DL / IEEE Xplore / PubMed / Scopus で統合クエリ検索を実行し、Zotero 経由でエクスポート。
- 生データ: `ResearchVR2.csv`（**14,385件**）。

### 2. スクリーニング Phase 1〜3（`pipeline.py` 実行済み）

```
14,385 件（生データ）
  → Phase 1 重複削除（DOI/Key/Title）      : -1,943 → 12,442 件（step1_dedup.csv）
  → Phase 2 Venueランク（CORE A/A*・SJR Q1）: -9,584 →  2,858 件（step2_rank_included.csv）
  → Phase 3 キーワード除外（AR/技術論文/臨床）: -1,074 →  1,784 件（step3_kw_included.csv ★最終候補）
```

- 実行ログ: `pipeline_log.txt`（除外キーワードごとの件数内訳あり）

### 3. 追加分析（`simulate_screening.py`、読み取り専用）
- **タスク1A（引用数足切り）:** CSVに引用数列が無いため最悪ケースのみ。2023年以降のフェイルセーフで754件残存。→ 引用数の外部取得が必要（未着手）
- **タスク1B（KWスコア足切り）:** 3カテゴリスコアで 0点=409件 / 1点=1,048件 / 2点=302件 / 3点=25件。Cat3（スケール知覚KW）ヒット率が3.4%と極端に低い（Abstract欠損 550件=30.8% の影響大）
- **タスク2（DB別集計）:** ACM 654 / IEEE 436 / Scopus系 652 / その他 42。PubMed/PsycInfo表記は0件（Scopus経由で吸収されたと推定）

### 4. 年次分布の可視化（`year_distribution.py`）
- `year_distribution.png` 生成済み（総計・DB別積み上げ・DB別折れ線）。**未コミット**。
- 傾向: 2020年以降が急増（2020-22: 442件、2023-24: 430件、2025-26: 324件）。

### 5. 関連ツール `../docs-system`（Next.js、別リポジトリ相当）
- Semantic Scholar 検索 → 引用ネットワーク可視化（D3）→ Supabase 保存 + R2 にPDF保存、CORE/SJR ランク付与、という文献ブラウザを実装中。
- サーベイ本体との接続（1,784件の取り込み等）はまだ。`../DocsSystem` は空フォルダ（廃棄した試作跡）。

---

## まだやっていないこと（rule.md のプロトコルとの差分）

1. **Phase 3.5: LLM（Gemini）による要旨判定** — rule.md の本来の Phase 3。
   - HCI系: 保守的（再現率優先）／心理系: PICOS厳格照合（適合率優先）の分岐戦略。**未実装・未実行**。
   - 現状の「Phase 3」はキーワード正規表現による機械的除外であり、rule.md の Phase 2 相当に留まる。
2. **引用数の補完** — Semantic Scholar API で DOI → citationCount を取得し CSV に列追加（README末尾にコード例あり）。足切りシミュレーションの実質化に必須。
3. **AI判定の目視検証** — 無作為抽出サンプルの著者チェック（rule.md 記載の信頼性担保手続き）。
4. **Phase 4: 全文適格性評価** — PICOS基準（健常成人 / HMD+スケール操作 / 比較条件 / 定量指標 / 実証研究）での全文精査。
5. **Taxonomy コーディング** — 採択文献への3軸分類の付与。
6. **分析・考察** — 年代×Taxonomy変遷、Venue別トレンド、タスク×モダリティのクロス集計、非視覚パラメータ体系化、Social VR・個人差の観点（rule.md §4）。
7. **PRISMA フロー図の作成**、rule.md 冒頭の「○○件」の確定値への置換。

## 既知の課題・メモ

- **Abstract欠損が30.8%（550件）** — KWスコアやLLM判定の精度に直結。Crossref/S2 APIでのAbstract補完を検討。
- **Phase 2 の未判定（Unmatched）5,126件をまとめて除外している** — 2026-07-16 に上位50 Venue（2,152件=42.0%をカバー）を監査した結果、Levenshtein類似度0.85以上で A*/A/Q1 に一致する「表記ゆれ脱落」は **0件**（`outputs/unmatched_venues_top50.csv`）。上位は VRCAI/VRIC 系 proceedings・CHI Extended Abstracts・Venue名空欄(233件) が中心。残り58%のロングテールは未監査。
- **rule.md と実装の軽微な乖離:** rule.md は「SJR Q1原則・不足時Q2まで」だが実装は Q1 のみ。CORE も A/A* のみ。本文執筆時に整合させること。
- **KW=1点の残存層480件（2023年以降）** — VR環境KWのみヒット。Phase 4 で要注意層。
- Windows での実行は `python -X utf8` を付けること（文字化け防止）。

---

## セッションログ（新しいものを下に追記）

### 2026-07-16
- 約1.5ヶ月ぶりの再開。リポジトリ全体を棚卸しして本ログ（PROGRESS_LOG.md）を作成。
- Claude Code 用 skills（survey-resume / survey-pipeline / survey-log）を `../.claude/skills/` に作成。
- 次のアクション候補（優先度順）を策定:
  1. 引用数・Abstract の API 補完（Semantic Scholar）
  2. LLM要旨スクリーニング（rule.md Phase 3）の実装・実行
  3. 目視検証 → Phase 4 全文評価へ
- 未コミットの `year_distribution.py` / `.png` と本ログのコミット推奨。

### 2026-07-16 (2) — Known-Item Test 基盤の整備(ACM Computing Surveys 投稿準備)
- **方針決定: 包含/除外判定に AI/LLM を使わない(再現性要件)。全スクリーニング基準は決定論的とする。**
  rule.md の「Phase 3: AI支援による要旨判定」は本方針に合わせて再設計が必要(rule.md 未修正、要対応)。
- `known_items.md` 作成 — quasi-gold standard テンプレート(目標15〜25件、Kitchenham 最低10件)。**著者の記入待ち。**
- `scripts/known_item_test.py` 作成 — 既知文献の step0〜3 生存判定。DOI→正規化タイトル→Levenshtein≥0.9(候補提示のみ、自動確定なし)。
  出力: `outputs/known_item_test.csv` + `known_item_analysis.md`(脱落分析レポート自動生成) + recall サマリ。
  実在論文6件でE2E検証済み(step0脱落/step2未照合/step2 Q2/step3誤爆/FUZZY の全経路動作確認、テストデータは削除済み)。
- `scripts/unmatched_venue_audit.py` 作成・実行 — Venue未照合 5,126件(ユニーク1,813種)の上位50件を監査。
  **結果: 表記ゆれによる高ランク(A*/A/Q1)脱落は0件**(上位50=2,152件、全体の42.0%)。→ Threats to Validity の証拠として `outputs/unmatched_venues_top50.csv` を使用可。
  - 特記: CHI Extended Abstracts 系が変種合計で約190件。EA≠フルペーパーなので除外維持が妥当だが、意図的判断として本文に明記すること。
  - 特記: Venue名空欄が233件(未照合の4.5%)。別途原因調査の価値あり。
- 制限事項の記録: DB別の統合前生データは保存されておらず(`Library Catalog` 列も全件空)、step0 は統合後 `ResearchVR2.csv` での存在判定+URL/DOIからのDB推定となる。
- skills を `.claude/skills/`(リポジトリ内)へ移動し git 管理下に。
- **次回やること(優先度順):**
  1. known_items.md に15〜25件を記入(Intro/RW/Taxonomy の引用予定から逆算、境界事例も含める)
  2. `python -X utf8 scripts/known_item_test.py` を実行し、known_item_analysis.md の脱落分析に基づき検索式/ホワイトリスト/除外KWを修正
  3. step2 Q2 脱落が出た場合、rule.md「Q1原則・不足時Q2」と実装「Q1のみ」の乖離をどちらに寄せるか決定
  4. rule.md の Phase 3(AI判定)を決定論的手法へ書き換え
