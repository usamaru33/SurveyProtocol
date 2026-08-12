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
| 2026-05-25 | README.md 作成。Phase 1〜3 実行済み（ResearchVR2.csv, 14,385件 → 1,784件） |
| 2026-05-27 | 別プロジェクト `../docs-system`（Next.js 文献ブラウザ）を作業 |
| 2026-07-16 | 約1.5ヶ月ぶりに再開。本ログと Claude Code skills を整備。**Rev.2: AI判定を全面廃止** |
| 2026-07-17 | Rev.3〜Rev.6。IEEE更新検索の統合（→ ResearchVR3.csv, 14,682件 → 1,827件）、SJR Q1確定、実行クエリの判明、G1拡張と Venue照合の再設計 |
| 2026-07-21 | Rev.7 検索方法論の検証。プロトコル文書を `docs/` へ集約 |
| 2026-07-22 | **Rev.8: DB構成を3DB（ACM/IEEE/Scopus）に確定、PubMed 不使用**。API検索ツール整備 |
| 2026-07-27 | APIキー投入。Scopus scope の実測（TITLE-ABS 2,533 vs TITLE-ABS-KEY 4,727） |
| 2026-07-30 | Scopus 第2波を本実行（2,542件）。スノーボーリング自動化 |
| 2026-07-31 | README 全面見直し。§8 スノーボーリングを新設 |
| 2026-08-01 | **Rev.9: 評価者3名のペア分担を確定**（Phase 3b / Phase 4） |
| 2026-08-02〜03 | **ACM 第2波を取得完了（9,630件）**。年スライス方式の確立、gold set の誤り2件を修正 |

---

## 完了していること

### 1. プロトコル（Rev.12 まで確定）
- **DB構成: 3DB（ACM DL / IEEE Xplore / Scopus）**。PubMed は Rev.8 で不使用に確定、PsycINFO はアクセス制約で不使用。
- **判定に AI/LLM は不使用**（Rev.2）。Phase 3a は決定論的キーワード除外、Phase 3b/4 は人手。
- **Venue 基準: CORE A*/A のみ + SJR Q1 のみ**（Rev.4）。Q2脱落826件は Threats で報告。
- **検索 scope: TA（Title-Abstract）**（Rev.10 で最終確定）。第1波のみ scope が異なる（Scopus=TAK / IEEE=広域、Rev.11）。
- **評価者3名のペア分担 + ペアワイズ Cohen's κ の平均**（Rev.9）。
- 変更履歴は `docs/protocol_changelog.md`。**`rule.md` 本文は Rev.11 までを反映済み（2026-08-11）。**

### 2. 検索データ

| 波 | DB | 件数 | ファイル |
|---|---|---|---|
| 第1波 | ACM DL | 7,997 | `raw/acm.csv` |
| 第1波 | IEEE Xplore | 1,276 + 297（更新検索） | `raw/ieee.csv` / `raw/IEEE_2025-2026.csv` |
| 第1波 | Scopus | 4,331 | `raw/Scopus.csv` |
| 第1波 | ~~PubMed~~ | 781（Rev.8 で不使用） | `raw/PubMed.csv` |
| **第2波** | **Scopus** | **2,542** | `raw/scopus_wave2_20260730.csv` |
| **第2波** | **ACM DL** | **9,630** | `raw/acm_wave2_20260803.csv` |
| **第2波** | **IEEE Xplore** | **361** | `raw/ieee_wave2_20260810.csv` |

- 第2波は Rev.6 の G1拡張クエリ。ACM は **title検索 6,013 + abstract検索 8,331 の和集合**（`docs/search_strings.md` にスライス内訳）。
- Zotero 往復の無損失を3例で実測（Scopus 2,542 / ACM 9,630 / IEEE 361 とも一致）。
- **統合生データ `ResearchVR4.csv` = 26,434件**（`scripts/merge_raw.py`、Source_DB 列つき、PubMed 除外）。

### 3. スクリーニング Phase 1〜3（**Rev.12 公式再実行済み・凍結解除**）

```
26,434 件（ResearchVR4.csv = 3DB × 第1波+第2波）
  → Phase 1 重複削除        : -8,092 → 18,342 件
  → Phase 2 Venueランク      : -14,317 →  4,025 件
  → Phase 3 キーワード除外    : -1,366 →  2,659 件（step3_kw_included.csv ★最終候補）
```

- **2026-08-12 に正規化改修（Rev.12）を適用して公式再実行**。2026-07-17 15:06 以来の凍結を解除した。
  旧値（14,682→12,543→2,909→1,827）は第1波・4DB 前提であり**以後は使用しない**。
- Phase 3 内訳: Cat1 非没入 568 / Cat2 技術・非実証 113 / Cat3 臨床・医療 775。
- Phase 2 出力に `Match_Stage` / `Match_Guard_Note` を追加（誤照合を可視化する監査列）。
  unmatched 9,066件のうちガード起因は 865件（9.5%）。
- **Phase 3b の工数は 3名ペア分担で約 1,773件/人**（2,659×2÷3）。

### 4. 検証基盤
- **Known-Item Test**（`scripts/known_item_test.py`）: gold set = `self_scale_references.csv`（in-scope 12件）。
  現在 step0 **66.67%**（8/12、目標 ≥80%）→ step2 **25.00%**（Rev.12 再実行後も同値）。
  **Rev.12 で脱落の性質が変わった**: venue 脱落5件の内訳が「照合漏れ3件」→「照合漏れ1件（#7のみ）/
  ランク不足3件」へ。#8・#13 は正しく照合したうえで CORE B・C だった。脱落分析は `known_item_analysis.md` に自動生成。
- **エクスポート完全性の監査**（`scripts/export_completeness_audit.py`）: 打ち切り検出・重複・
  期待件数との突き合わせ・gold set 照合（HIT/SUSPECT/MISS）。ACM の1,000件打ち切りを検出した実績あり。
- **統合生データの生成**（`scripts/merge_raw.py`）: `Source_DB` 列を付与。PubMed は既定で除外。
- **年スライス .bib の統合**（`scripts/merge_bib.py`）: 引用キー単位で一意化。
- Venue 監査一式（`venue_match_audit.py` / `normalization_collision_audit.py` / `unmatched_venue_audit.py` /
  `venue_dropped_audit.py`）と出力 CSV 群。

### 5. API 検索の自動化
- `scripts/db_search_scopus.py`（**稼働中**）/ `scripts/db_search_ieee.py`（403 で停止中）/
  `scripts/api_search_common.py`（クエリ生成・polite_get・RIS出力・.env読み込み）。
- `scripts/snowball_search.py`（S2 引用探索、**1ホップ実行済み** 1,854行/新規1,433件。列追加のため要再実行）、`scripts/enrich_abstracts.py`（Abstract補完、少数件試験のみ）。

### 6. 関連ツール `../docs-system`（Next.js、別リポジトリ相当）
- Semantic Scholar 検索 → 引用ネットワーク可視化（D3）→ Supabase + R2。**サーベイ本体とは未接続。**
  `../DocsSystem` は空フォルダ（廃棄した試作跡）。

---

## まだやっていないこと（優先度順）

### A. データ取得 — 残り1件
1. **IEEE 第2波（379件）のエクスポート** — 上限2,000件に収まるので分割不要。
   `raw/ieee_wave2_YYYYMMDD.csv` に配置。**これが最後の未取得データ。**
   （API 経由は `ERR_403_DEVELOPER_INACTIVE` で停止中のため手動エクスポート）

### B. 統合と再実行（IEEE が揃い次第）
2. `merge_raw.py` で `ResearchVR4.csv` 生成 → `known_item_test.py` で step0 recall 実測
   → **TA 維持か TAK 移行かの判断**（現 69.23% / 目標 ≥80%）
3. Venue 正規化の改修（`normalization_design.md` 案6+1+3+4）を `pipeline.py` に適用
4. **公式再実行** → step ファイル更新 → PRISMA 数値確定
5. `rule.md` 本文へ Rev.8 分（3DB構成・scope=TA・Threats）を反映
6. 和集合方式の逸脱を `protocol_changelog.md` に記録（Rev.10 候補）

### C. スクリーニング本体
7. **Phase 3b: Title/Abstract 二重スクリーニング** — 評価者3名のペア分担、各文献を2名が独立評価、
   ペアごとの Cohen's κ の平均を報告（Rev.9）。工数は **約1,773件/人**（2,659件×2÷3）。
   - ~~判定シート様式が**未作成**~~ → **作成済み（2026-08-12）**。
     `scripts/make_screening_sheets.py`（生成）/ `scripts/score_screening.py`（κ算出・協議リスト）/
     `docs/screening_protocol.md`（運用手順）。**評価者ごとに別ファイル**にして独立性を担保。
     ブロック割当は決定論的（キーの MD5 mod 3）。シートは生成済みで**記入待ち**
     （ブロック1 851件 / 2 887件 / 3 921件）
   - キーワードスコアは読む順序のトリアージにのみ使用可。自動除外はしない
   - **着手前の判断事項**: 要旨欠落 567件（21.3%、うち513件がACM）をタイトルのみで判定するか、
     `enrich_abstracts.py` で補完してから始めるか
8. **Phase 4: 全文適格性評価** — PICOS基準。体制は Phase 3b と同一。
   **除外理由（PICOS のどの基準に抵触したか）を1件ずつ記録**すること
9. **Taxonomy コーディング** — 採択文献への3軸分類の付与
10. **分析・考察** — 年代×Taxonomy変遷、Venue別トレンド、タスク×モダリティ、非視覚パラメータ体系化
11. **PRISMA フロー図の作成**、`rule.md` 冒頭の「○○件」の確定値への置換

### D. 補助タスク（並行可能）
12. **スノーボーリング実行** — `snowball_search.py` → `outputs/snowballing_log.csv` →
    `picos_decision` 記入。Venue脱落6件の回収が目的。**未実行**
13. **Venue suspect の目視確認** — 優先度P1 = 91ユニーク/240件（`outputs/venue_suspect_matches.csv`）
14. **gold set の in-scope 拡充** — 13件 → 15〜25件。1件が recall を7.7%動かす粒度の粗さを解消する
15. **ACM Abstract 補完の要否判断** — 検索の網羅性とは別問題と判明したため優先度は低いが、
    Phase 3b で人が要旨を読む以上は必要（第2波ACMは97.6%充足なので対象は第1波分）
16. **引用数の補完** — S2 API で citationCount 取得。**専用スクリプトは未整備**。
    採用にはプロトコル改訂が必要
17. `known_item_test.py` の照合ロジック改善 — タイトル一致時に DOI が食い違う場合に警告する
    （gold set #13 の偽陽性を見逃した原因。`export_completeness_audit.py` 側では対応済み）

## 既知の課題・メモ

- **Abstract欠損** — 最終候補での欠損は 30.8%（550件、旧データ）。**コーパス全体では ACM 由来の欠落が 7,655件**（全件DOIあり）。
  補完手段は `scripts/enrich_abstracts.py`（Crossref→S2）。2026-07-30 の20件試験で **11/20（55%）成功・全て S2 経由**、
  Crossref 経由は0件（該当ACM論文に Crossref 側の Abstract が元々無い。仕様であって不具合ではない）。本実行は未実施。
  なお第2波 Scopus（`raw/scopus_wave2_20260730.csv`）は **Abstract 充足率 100%** で、この問題は ACM に固有。
- **Phase 2 の未判定（Unmatched）をまとめて除外している** — 現行値は **5,166件**（ResearchVR3。監査当時は 5,126件）。
  2026-07-16 に上位50 Venue（2,152件=42.0%をカバー）を監査した結果、Levenshtein類似度0.85以上で A*/A/Q1 に一致する「表記ゆれ脱落」は **0件**（`outputs/unmatched_venues_top50.csv`）。上位は VRCAI/VRIC 系 proceedings・CHI Extended Abstracts・Venue名空欄(233件) が中心。残り58%のロングテールは未監査。
- ~~**rule.md と実装の乖離（SJR Q2）— 判断待ち**~~ → **解決済み（Rev.4, 2026-07-17）: SJR は Q1 のみ採用に確定。**
  Q2 による脱落 **826件/332誌**（`outputs/sjr_q2_excluded_venues.csv`）は Threats to Validity で報告する。
  上位は臨床系＋LNCSだが、IEEE Trans. on Haptics(13)・Computer Animation and Virtual Worlds(15)・
  Multisensory Research(3)・QJEP(6)・Neuropsychologia(5) 等の主題関連誌を含むため、報告時に具体名を挙げること。
  CORE 側は「A*/A のみ」で確定済み（Rev.2）。
- **KW=1点の残存層480件（2023年以降）** — VR環境KWのみヒット。Phase 4 で要注意層。
- **公式 step ファイルは凍結中（重要）** — 現行の `step*.csv` / `pipeline_log.txt` は **2026-07-17 15:06 の実行結果**であり、
  同日 16:27 に追加した **Step 0 エイリアス表（`venue_aliases.csv`）を通していない**（ログに alias 統計行が無いことで確認可能）。
  エイリアス適用後の scratchpad 試験値は **2,917 → 1,831件**。公式再実行は第2波再検索の完了後にまとめて行う。
- **Venue照合の順序問題（未修正）** — Step A の CORE ファジー照合（≥0.82）が Step B の SJR 完全一致より先に走るため、
  ジャーナルが CORE の類似会議名に誤マッチしうる。最大の実例は **PACM HCI 82件**。
  正規化の同名衝突は 899キー・採否反転 426件（データ出現74キー、`venue_aliases.csv` に MANUAL 行として自動追記済み）。
  恒久対策は `normalization_design.md` の6案（推奨: 案6順序修正 + 案1種別マーカー + 案3短キーガード + 案4サニティチェック）で、**公式再実行時に適用**。
- **Known-Item recall が目標未達** — step0 **69.2%**（9/13、目標 ≥80%）→ step2 **23.1%**（3/13）。
  step0 の脱落4件は検索式・DBカバレッジ（Rev.6 の G1拡張で対処）、**step2 の脱落6件は Venue フィルタ**が主因で、
  回収手段はスノーボーリング（`outputs/venue_dropped_known_items.csv`）。第2波再検索後に再測定する。
- **Venue suspect 照合の目視確認が未了** — 優先度P1 = 91ユニーク/240件（`outputs/venue_suspect_matches.csv`）。著者タスク。
- **DBエクスポートは黙って打ち切られる（重要な教訓）** — ACM DL は **1,000件**、IEEE Xplore は **2,000件**が上限で、
  超過分は**警告なしに切り捨てられる**。しかも打ち切りは新しい年に偏るため、そのまま使うと
  「recall が低い」という誤った結論が出る。対策は出版年でのスライスと、
  **UI表示ヒット数とエクスポート実件数の突き合わせ**（`scripts/export_completeness_audit.py`）。
  2026-08-02 の ACM で実際に発生し、取り直しにより計164件を回収した。
- **ACM は title 検索と abstract 検索の和集合（Rev.9 時点）** — 群ごとに `(Title:G OR Abstract:G)` を
  入れ子にした単一クエリではないため、**フィールド横断の一致（G1はタイトル・G2は要旨のみ、等）を取りこぼす**。
  gold set 13件中11件が Abstract のヒットに依存しており、机上の懸念ではない。
  **PRISMA-S / Threats to Validity に逸脱として明記すること。**
- **gold set のメタデータ品質** — 2026-08-03 に #10（DOI誤記）と #13（3論文の情報が混在）を発見・修正した。
  **他の項目にも同種の誤りが残っている可能性がある。** in-scope を拡充する際は
  DOI・年・掲載誌・著者の整合を確認すること。検出には `export_completeness_audit.py` の
  SUSPECT 判定（タイトル一致だが DOI 不一致）が使える。
- ~~**`known_item_test.py` はタイトル一致の偽陽性を検出できない**~~ → **解決済み（2026-08-12）**。
  両方向の偽陽性を検出するようにした:
  ① タイトル一致だが DOI 食い違い → `SUSPECT`（捕捉と数えない）
  ② **DOI 一致だがタイトルが別物** → `SUSPECT`（gold set の DOI 誤記で実在する別論文を掴む case。#13 の実例）
  ③ DOI 一致でタイトルに表記差 → `DOI(表記差)` として recall には算入しつつ `[METADATA]` 警告
  判定境界 `DOI_TITLE_SUSPECT_THRESHOLD = 0.60` は実測で決定（同一論文の表記差 0.736 /
  誤DOIによる別論文 0.330）。導入時に **gold set #6 のタイトル誤記を新たに検出**し修正した。
  `export_completeness_audit.py` と結果が一致することを確認済み（HIT 8/12・SUSPECT 0）。
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

### 2026-07-16 (3) — プロトコル改訂 Rev.2 と検索記録の現状把握
- **rule.md 改訂(Rev.2)**: 「Phase 3: AI支援による要旨判定」を削除し、
  Phase 3a(決定論的キーワード除外・全パターンの追加理由をPICOS対応表で明記)+
  Phase 3b(人手2名独立のTitle/Abstract二重スクリーニング・Cohen's κ 報告・不一致協議)に置換。
  HCI/心理の分岐フローは AI 戦略差に由来したため単一フローに統合。
  重複削除を Phase 1 として明文化、CORE「A以上」→「A*/A のみ」に表記確定。
  変更履歴は `protocol_changelog.md` に記録(CSUR 方法論セクション用)。
- **SJR Q2 乖離の判断材料を出力(判断は保留・TODO埋め込み済み)**:
  Q2脱落 = **823件/332誌**、全リスト `outputs/sjr_q2_excluded_venues.csv`。
  臨床系(Cat3でどのみち除外)+LNCS(131)が主だが、IEEE Trans. on Haptics(13)、
  Computer Animation and Virtual Worlds(15)、Multisensory Research(3)、QJEP(6)、Neuropsychologia(5) など主題関連誌あり。
- **検索記録の現状把握(結論: 全滅)**: 4DB すべてで verbatim 検索式・実行日・DB別ヒット数が未記録。
  PsycInfo は実行有無自体が不明。統合CSVに取得元DB列なし(URL/DOIによる出版社推定:
  ACM 8,345 / Scopus系 3,475 / IEEE 1,913 / 不明 650 / PubMed 2 — PRISMA報告には使用不可)。
- `search_strings.md` 作成(記録表テンプレート+現状の判明分+REQUIRES RE-RUN 明記)。
- `search_replication.md` 作成(DB別の検索構文・エクスポート形式・文字コード・上限・ID列・
  統合時のDB間/DB内重複の区別、再実行後チェックリスト)。
- **次回やること(優先度順):**
  1. SJR Q2 の扱いを確定(outputs/sjr_q2_excluded_venues.csv を目視)→ rule.md の TODO 解消 + changelog Rev.3
  2. known_items.md 記入 → Known-Item Test 実行(検索再実行の前に現行データで一度回し、検索式改訂の要否も判断)
  3. search_replication.md の手順で全DB再検索(同日実行・DB別生データを raw/ に保全・Source_DB列付与)
  4. 再検索データでパイプライン再実行 → PRISMA フロー図を上段から再構築

### 2026-07-16 (4) — 訂正: 検索データは Zotero でDB別コレクション管理されていた
- 著者より: 検索結果は Zotero で管理し、**取得元DB(ライブラリ)ごとにフォルダ分けしている**。
  リポジトリの CSV はその統合エクスポート。→ **「全DB再検索が必要」という (3) の結論を訂正**。
- `Date Added` 分析: 取り込みは **2025-12-25(1,276件)/ 2026-05-15(13,109件)の2波**。
  検索実行日の上限近似として使用可(2波の経緯は要著者確認)。
- `search_replication.md` を再構成: **Option A = Zotero コレクション別エクスポートによる復元(推奨・再検索不要)**、
  Option B = 再検索(verbatim 検索式の確定が必要な場合のみ)。search_strings.md も同様に更新。
- 依然として欠けるのは **verbatim 検索式・使用フィルタ**のみ(Zotero に保存されない情報)。
- **著者への依頼事項:**
  1. Zotero の各DBコレクションを CSV エクスポートして `SurveyProtocol/raw/` に保存
     (ファイル名: `<db>_zotero_YYYYMMDD.csv`)+ コレクション別件数を search_strings.md に記入
  2. 検索式の手元記録(メモ・DBアカウントの検索履歴等)の有無を確認
  3. 2025-12-25 と 2026-05-15 の2回取り込みの経緯(予備検索+本検索?追加DB?)を教える

### 2026-07-17 — PRISMA 上段の確定(raw/ 提供を受けて)
- 著者が `raw/` に Zotero コレクション別エクスポート4本を配置(acm/ieee/PubMed/Scopus)。
- `scripts/raw_db_audit.py` 作成・実行(`outputs/raw_db_audit.csv`):
  - **Records identified 確定: ACM 7,997 / IEEE 1,276 / PubMed 781 / Scopus 4,331 = 計 14,385**
  - 統合CSVと Zotero Key で **1:1 完全一致**(欠落・混入・複数コレクション所属 すべて0件)→ 統合エクスポートの完全性を確認
  - **2波の経緯が判明: 2025-12-25 = IEEE のみ / 2026-05-15 = ACM+PubMed+Scopus**
  - DB間重複: PubMed∩Scopus 606 / Scopus∩IEEE 352 / Scopus∩ACM 142 / PubMed∩IEEE 39 / ACM∩IEEE 0 / ACM∩PubMed 0
  - **PsycInfo は未実行が確定**(コレクション無し)。不実行判断の理由を本文に書く必要あり
- `scripts/known_item_test.py` を拡張: step0 で **どのDBコレクションが既知文献を捕捉したか**を
  `step0_source_dbs` 列に出力(raw/ 存在時のみ)。スモークテスト済み(例: IEEE VR 2018 論文 → 'ieee; Scopus')
- search_strings.md に確定値を記入(残りの未記録は verbatim 検索式・フィルタのみ)
- **新たな課題: 検索時点の非対称** — IEEE のみ 2025-12 実行で他DBより約5ヶ月古い。
  IEEE の更新検索(差分追加)か Threats to Validity 明記かの判断が必要
- **次回やること(優先度順):**
  1. SJR Q2 の扱いを確定(前日から継続、outputs/sjr_q2_excluded_venues.csv)
  2. IEEE 検索時点の非対称への対応方針を決定(更新検索 or Threats 明記)
  3. verbatim 検索式の手元記録を確認(無ければ Option B で該当欄のみ確定)
  4. known_items.md 記入 → Known-Item Test 実行

### 2026-07-17 (2) — IEEE更新検索の統合(Rev.3)と Known-Item Test 初回実行
- **IEEE更新検索を統合**: `raw/IEEE_2025-2026.csv`(297件、出版年2025:201/2026:96)。既存とDOI重複196、**新規101件**。
  `ResearchVR3.csv`(14,682件)を新入力としてパイプライン再実行:
  **14,682 → 12,543(-2,139) → 2,909(-9,634) → 最終候補 1,827件(+43、全てIEEE分)**。
  README・search_strings.md 更新、protocol_changelog.md に Rev.3 記録。検索時点の非対称は解消。
  year_distribution.png・outputs/sjr_q2_excluded_venues.csv(Q2脱落 826件/332誌に微増)を再生成。
- **Known-Item Test 初回実行**(`self_scale_references.csv`、18件。スクリプトは列エイリアス・--items・
  最新 ResearchVR*.csv 自動選択に対応拡張):
  - **recall: step0 50%(9/18)→ step2 16.7%(3/18)→ 最終 16.7%(3/18)**
  - **発見1(検索式のギャップ)**: 多感覚系の必須文献4件(footsteps音・action sounds・audio-tactile・足裏振動)が
    step0 で全滅。G3(スケール知覚語)に body weight/height, arm dimension 等が無く、非VRの心理実験は G1 も不成立。
    Being Barbie(原典)も脱落(タイトルに VR 語なし。G1 に "head-mounted display"/"immersive" が無い)。
  - **発見2(実行検索式への疑義)**: 「The effects of eye height and self-avatars on distance estimation in
    virtual environments」はタイトルだけで3コンセプト群すべて命中するのに生データに不在
    → 実際に実行された検索式が文書化クエリと異なる疑い。verbatim 検索式の確認が急務。
  - **発見3(Venueスクリーニングの実害)**:
    - Kilteni 2012(SoE定義・必須)が「Presence 誌 → CORE『Annual International Workshop on Presence』(C)」への
      **誤照合**で除外(同誌の誤照合は本体データで29件)。なお Presence:TVE は SJR Q3 のため正しく照合しても現基準では除外
      → 分野の歴史的中核誌がランク基準で落ちる構造問題。
    - Gulliver's virtual travels が Cognitive Processing **Q2** で脱落 → Q2判断に実害の証拠。
    - APGV/MIG/ACM ICPS の3件が Venue 未照合で脱落(ロングテール未照合にも関連文献が実在)。
  - 書籍(Gallagher 2005)・非VR理論(Tsakiris 2010)の step0 脱落は想定内(検索対象外)。
    known_items の「検索で拾えるべき群」と「手動追加の背景文献群」を分ける列の追加が必要。
- **次回やること(優先度順):**
  1. **検索式の再設計判断**: G1 に "head-mounted display"/"immersive"、G3 に body weight/height,
     arm/limb dimension, body representation 等の追加を検討(known_item_analysis.md の提案参照)→ 追加時は再検索
  2. **SJR Q2 の確定**(Gulliver 脱落という実害が判明。Q1+主題直結Q2誌の個別採用が有力)
  3. Venue誤照合(Presence 29件)への対処: CORE照合のファジー閾値/頭字語処理の見直し、または例外表
  4. self_scale_references.csv に「検索スコープ内/外」列を追加し recall を層別に再計算

### 2026-07-17 (3) — SJR Q1のみ確定(Rev.4)・実行検索式の判明(Rev.5)・脱落原因の完全分離
- **SJR は「Q1のみ」で著者決定(= A案)** → rule.md の TODO 解消、changelog Rev.4。
  Q2脱落(826件/332誌、Gulliver 論文含む)は Threats to Validity で報告する方針。実装・数値の変更なし。
- **実行された検索式が判明(著者提供)**:
  `("Virtual Reality" OR "VR" OR "HMD") AND ("Avatar" OR "Body" OR "Embodiment") AND ("Size" OR "Scale" OR "Height" OR "Distance")`
  → rule.md 旧版の詳細クエリは**計画段階のもので実行されていなかった**(Rev.5 で記録訂正)。
  実行版は G2/G3 が広く(単独語)、**G1 に "Virtual Environment"/"head-mounted display"/"immersive" が無い**。
  前回の「実行検索式への疑義」はこれで解決。
- **known_item_test.py を実行版クエリに更新**し、self_scale_references.csv に `SearchScope` 列を追加
  (background=書籍・非VR理論/心理5件は recall 分母から除外)。**in-scope recall: step0 69.2%(9/13)→ 最終 23.1%(3/13)**
- **step0 脱落4件の原因を完全分離**:
  - **DBカバレッジ欠落(3件)**: [9][12][18] すべて **Frontiers in Virtual Reality** 掲載。
    [9] はタイトルが実クエリに完全適合するのに不在 → 検索対象DBが同誌を索引していないことが確定。
    **同誌は SJR Q1** なので、捕捉できれば Phase 2 も通過し最終候補まで残れる。
  - **クエリG1ギャップ(1件)**: Being Barbie(PLoS ONE = Scopus/PubMed 索引済み・SJR Q1)。
    ライブラリ追加では直らず、**G1 拡張("head-mounted display"/"immersive"等)+再検索が必要**。
- **次回やること(優先度順):**
  1. **検索改訂 Rev.6 の実行判断(著者)**: (i) G1 拡張クエリで全DB再検索(第2波)、
     (ii) Frontiers in Virtual Reality のカバレッジ確保(Scopusの索引状況確認 or 誌内検索を
     supplementary source として追加、PRISMA の Other sources 行で報告)
  2. Venue誤照合(Presence→COREワークショップ、29件)と未照合3件(ACM ICPS/APGV/MIG)への対処
     (エイリアス表 or 例外表。Presence:TVE は SJR Q3 のため救済しても現基準では除外という論点も記録)
  3. Phase 3b(人手二重スクリーニング)の準備(データセットが検索改訂で動くため、Rev.6 確定後に着手)

### 2026-07-17 (4) — Rev.6 実装: G1拡張・Venue照合の再設計・誤照合監査
- **著者確定(Rev.6)**: 検索式 G1 を拡張(+"head-mounted display"/"head mounted display"/
  "Virtual Environment*"/"immersive virtual"。"immersive"単独は precision 悪化のため不採用)。
  スコープ不変。rule.md §3.1・search_strings.md に反映。**再検索は実施待ち**。
- **誤照合監査(`scripts/venue_match_audit.py` 新規・実行済み)**:
  - 照合成功7,377レコードの全数を段階別に再導出: SJR exact 3,137 / CORE exact 2,525 /
    **CORE fuzzy 966 / SJR ISSN 532 / CORE acronym 217**
  - **非完全一致が採否を左右: 1,183件(採用590/除外593)**。誤照合疑い 238ユニーク/707件
    → `outputs/venue_suspect_matches.csv`(著者目視待ち)
  - Presence 誤照合の正体は fuzzy ではなく**正規化同名衝突(exact_norm)**と判明
    → fuzzy 監査では原理的に検出不能なタイプ
- **監査設計の穴を changelog に自己申告**: 2026-07-16 の Task 4 監査は未照合側のみ対象で、
  誤照合(false positive)は検出できていなかった。「A*/A/Q1脱落0件」は Venue フィルタ全体の
  妥当性を保証しない。
- **`venue_aliases.csv` ドラフト作成(著者確認待ち)+ pipeline.py をエイリアス最優先に改修**
  (生文字列一致→正規化一致の2段。正規化キー衝突は警告して exact 側で解決):
  - Presence誌29件: CORE C 誤照合 → SJR Q3(基準による除外)に是正
  - **新発見: TAP誌(ACM Transactions on Applied Perception)49件が SAP シンポジウムとの
    正規化同名衝突で CORE B 誤照合** → SJR Q2 に是正(基準による除外)
  - **旧称 IEEE Virtual Reality Conference(2007〜2011)の8件を A* として救済**
  - scratchpad での試験実行: 2,909→**2,917**(+8)、最終 1,827→**1,831**(+4)。
    **公式の step ファイルは未更新**(エイリアス表の著者確認+Rev.6再検索データ統合後に公式再実行)
- Frontiers in VR の supplementary source 手順を search_replication.md に追加
  (Scopus索引確認 → 無ければ誌内検索、PRISMA "other methods" 行で報告)。
- **次回やること(優先度順):**
  1. **著者**: venue_aliases.csv の目視確認(特に「著者確認待ち」行)+
     outputs/venue_suspect_matches.csv(238ユニーク)の確認
  2. **著者**: Rev.6 クエリで全DB再検索(第2波)+ Scopus の Frontiers in VR 索引確認
     → raw/ に第2波エクスポートを配置
  3. 第2波統合 → エイリアス有効で公式パイプライン再実行 → 全数値更新
  4. **Task 4: known_item_test.py で recall 再測定(目標: step0 in-scope ≥ 80%)**
  5. ICPS(46件)の個別解決(ISBN/Extra列から会議名復元)は優先度低として保留

### 2026-07-17 (5) — 正規化同名衝突の全数監査・suspect優先度付け・正規化設計文書
- **`scripts/normalization_collision_audit.py` 新規・実行**(公式stepファイルは不変更):
  - CORE∪SJR のキー空間を pipeline と同一手順で再構築し、同名衝突を全数列挙:
    **衝突キー899件**(現行データ出現 133キー/489レコード)、
    **採否が変わる衝突(rank_conflict)426件**(データ出現 74キー)
    → `outputs/normalization_collisions.csv` / `collisions_rank_conflict.csv`
  - rank_conflict 全426件を venue_aliases.csv に MANUAL 行として**自動追記**(冪等・著者確認待ち)
  - 実例: `sensors`(Sensors Q1 vs Journal of Sensors Q2、19件)、`ieee multimedia`
    (Trans. Q1 vs Symposium CORE C、10件)、`psychological research`(Q1 vs Q3、6件)等
  - 限界を文書化: データ側の短い誌名×リストエントリ型(Presence型)はリスト内衝突として
    現れないため本監査対象外 → venue_match_audit の P2 で捕捉
- **suspect 238ユニークに優先度付与**(venue_match_audit.py 拡張・再実行):
  **P1(採否が変わり得る)91ユニーク/240件**、P2(別会場疑い)29/90、P3(表記ゆれ)118/377。
  P1 最大は `Proceedings of the ACM on Human-Computer Interaction`(**82件**)が
  CORE『Indian Conference on HCI』に fuzzy 誤照合 — SJR に Q2 で正確に収載されているのに
  **CORE fuzzy が SJR exact より先に走る段階順序**が原因(新発見の設計問題)
- **`normalization_design.md` 作成**(提案のみ・実装保留): 現行正規化仕様の明文化、
  衝突原因5類型+段階順序問題の特定、改善案6件のトレードオフ表、
  エイリアス表 vs 正規化修正の議論(多層防御を推奨: 案6順序修正→案1種別マーカー+
  案3短キーガード→案4サニティチェック+エイリアス表+監査常設)
- changelog に Task C 注記(Rev.6 試験値は第1波のみの測定であり、エイリアス表の効果評価に
  使ってはならない)と衝突監査の追記を記録
- **次回やること(優先度順):**
  1. **著者**: normalization_design.md の採否判断(推奨: 案6+案1+案3+案4)と閾値決定
  2. **著者**: outputs/venue_suspect_matches.csv の P1(91件)から目視。
     venue_aliases.csv の自動追記426行は P1/HIGH 優先で確認
  3. **著者**: Rev.6 クエリで全DB再検索(第2波)+ Frontiers in VR の Scopus 索引確認
  4. 第2波統合 + 正規化改修(著者決定後)+ エイリアス確定 → 公式再実行(Rev.7)
     → known_item_test で recall 再測定(目標 step0 ≥ 80%)

### 2026-07-21 — 検索方法論5方針のデータ検証(Rev.7 判定・分析のみ、step ファイル不変更)
- **`methodology_decision_Rev7.md` 新規作成** — 暫定5方針を raw/*.csv・known_item_test.csv から
  決定論的に検証(LLM不使用)。scratchpad の分析スクリプトで A〜D を算出:
- **A. Known-item venue 内訳**: in-scope 13件 = VR/CG/HCI **9件(69%)** / 心理・神経系 **4件(31%)**
  (#4 PLoS ONE, #5 PLoS ONE, #6 PNAS, #14 Cognitive Processing)。心理接合点 seminal の
  **Botvinick&Cohen 1998・Lenggenhager 2007 は known-item にも raw 4DB にも不在** → background 追加を著者提案。
- **B. DB限界寄与**: **Scopus 無しで step0 消失する known-item 4件**(#5/#6/#10/#14、うち #10 は Scopus 単独=唯一源)。
  **PubMed の known-item 固有寄与は 0**(全 PubMed known-item は Scopus にも在る)。corpus固有推定:
  ACM 7,305 / Scopus 3,247 / IEEE 924 / **PubMed 175(22.4%)**。ペア重複 PubMed∩Scopus 606。
- **C. MeSH**: PubMed `Manual Tags` に MeSH 95%(743/781)格納=post-hoc 利用可。ただし
  **step0 欠落4件は MeSH で 0件も救えない**(3件 Frontiers VR=PubMed 非収載、1件 Being Barbie=raw 不在)。
- **D. フィルタ層**: 4DB は Zotero 同一スキーマ(枠組み実装可)だが中身が非対称 —
  **ACM Abstract 4.3%(342/7,997)**、usable Keyword は **PubMed(MeSH)のみ**(ACM Manual Tags は item-type 混入、
  Scopus 1.2%)、Automatic Tags 全DB 0%。Title のみ全DB 100%(唯一の共通分母)。
- **判定**: 方針1 支持(条件付き・PubMed の根拠弱い)/ 方針2 修正(一律TAK不可、共通分母=Title)/
  方針3 支持(要 degrade 設計)/ 方針4 修正・格下げ(MeSH 恩恵0、要ライブ差分)/ 方針5 支持(現 step0=69.2% 未達)。
- **副次発見**: 脱落主因は検索でも DB でもなく **Venue ホワイトリスト(step2 で 13件中 6件脱落)**。
  Zhou et al. の「学際取りこぼし」は消えず step2 へ移動しただけ、と Threats に明記して補強。
- `protocol_changelog.md` に **Rev.7** を記録。
- **次回やること(著者確認・優先度順)**:
  1. **著者**: PubMed corpus固有 175件の主題適合率サンプル(PubMed 独立正当化の可否)
  2. **著者**: PubMed で `"Virtual Reality"[Mesh]` OR 追加のライブ差分(MeSH corpus 便益=判断保留の解消)
  3. **著者**: ACM Abstract(4.3%)・Scopus Keywords(1.2%)の再エクスポート可否(方針2/3 の前提)
  4. **著者**: background known-item 追加(Botvinick&Cohen 1998, Lenggenhager 2007 等)+ known_items.md 正式化
  5. Rev.6 第2波再検索後に step0 recall 再測定(現 69.2% は第1波のみ)

### 2026-07-21 (2) — Rev.7 確定方針への是正タスク実行(4件、外部通信/step ファイル変更なし)
- **著者が Rev.7 方針を確定**: Scopus/PubMed 維持(PubMed は175件適合率で裏付け)、scope は
  一律TAK放棄→**TA基準**(Scopus Keyword 回収で TA+K 格上げ可)、フィルタ層は**利用可能フィールドのみ+degradeフラグ**、
  **MeSH は検索分岐に使わずフィルタ層内の任意recallブースタ+PRISMA-S報告に格下げ**、Known-Item Test 維持(目標 step0≥80%)。
- **Task1 エクスポート欠陥是正**: `search_replication.md` に「Rev.7 エクスポート欠陥の是正」節追加
  (ACM Abstract 4.3% → Zotero/ACM DL 再エクスポート優先・不可時 fallback、Scopus Keyword 1.2% → Author/Index Keywords 込み再エクスポート)。
  `scripts/enrich_abstracts.py` 新規(Crossref→S2 で DOI ベース Abstract 補完、**外部API=著者実行・コードのみ整備**)。
  `search_strings.md` に第2波の verbatim フィールド構文の必須記録ルール(Scopus=TITLE-ABS/PubMed=[tiab]/ACM=Title:Abstract:/IEEE=Document Title:Abstract:)。
- **Task2 PubMed固有175件**: `scripts/pubmed_unique_audit.py` 新規・**実行**。他DB(ACM/IEEE/Scopus/IEEE更新)に
  DOI・正規化タイトルとも不一致の **175件**を `outputs/pubmed_unique_175.csv` に出力(seed=42 無作為30件に judge_relevance 空欄+MeSH・Abstract抜粋)。適合率推定手順は docstring(判定は著者・LLM不使用)。
- **Task3 gold set 一本化**: 正式セット=`self_scale_references.csv` に確定、`known_items.md` 冒頭に注記。
  心理接合点の古典 2件を **background** 追加(#19 Botvinick&Cohen 1998 / #20 Lenggenhager 2007、非VR・recall分母外=検索とスノーボーリングの境界)。in-scope 15〜25件拡充は著者タスクとして明記。
- **Task4 Venue脱落6件のスノーボーリング**: `scripts/venue_dropped_audit.py` 新規・**実行** →
  `outputs/venue_dropped_known_items.csv`(分類実測: **unmatched 3(#7/#8/#13)/ below_rank 2(#3 Presence, #10 ICAT-EGVE)/ criterion 1(#14 Gulliver Q2)**)。
  `snowballing_protocol.md` 新規(シード選定・前後方探索2ホップ・PICOS採否・PRISMA右カラム "citation searching" 計上、drop_category別の扱い)。
- `methodology_decision_Rev7.md` に確定事項と成果物対応表を追記。`protocol_changelog.md` に「Rev.7 実行分」追記。
- **次回やること(著者、優先度順)**:
  1. `outputs/pubmed_unique_175.csv` の30件を judge_relevance 判定 → 適合率算出 → PubMed 独立正当化の可否を確定
  2. ACM Abstract / Scopus Keyword を再エクスポート(不可なら enrich_abstracts.py を著者実行)→ 充足率再測定
  3. `snowballing_protocol.md` に従い脱落6件を回収 → `outputs/snowballing_log.csv` 記録 → PRISMA 右カラム確定
  4. Rev.6 第2波再検索 + verbatim フィールド構文記録 → 公式再実行 → step0 recall 再測定(目標≥80%)
  5. 上記確定後に rule.md 本文へ反映(scope=TA、MeSH 格下げ、Threats に venue フィルタ取りこぼし)

### 2026-07-22 — Rev.8: DB構成を3DBに最終確定(ACM/IEEE/Scopus、PubMed不使用)
- **著者が Rev.8 を確定**: PubMed を不使用に確定(理由: 医学・治療目的の文献はスコープ外・
  主題適合性が低い。Rev.7の corpus固有175件分析は決定理由として使わず参考情報に格下げ)。
  PsycINFO はアクセス制約により従来どおり不使用、正当化を Scopus カバレッジ + Known-Item Test で補強。
- **Task1**: `protocol_changelog.md` に **Rev.8** を記録。`methodology_decision_Rev7.md` に
  「Rev.8 追記」節を新設(DB選定最終構成表、**PsycINFO不使用の正当化ドラフト**(Threats to Validity 転用可、
  #5/#6/#14 の Scopus 捕捉+#10 Scopus単独性を実証根拠に使用)、Rev.7分析(PubMed前提)の
  「参考情報」への位置づけ変更)。`search_strings.md`/`search_replication.md` の PubMed(§3)・
  PsycInfo(§5)手順を「Rev.8で不使用確定」と明記(削除せず経緯として保存)。
- **Task2(エクスポート欠陥是正)**: **Rev.7で整備済みのため追加作業なし**
  (`search_replication.md` §Rev.7是正 + `scripts/enrich_abstracts.py` は ACM/Scopus 向けで
  DB非依存、そのまま有効)。Keyword格上げの判断は「Rev.9候補」と呼称変更(Rev.8は既にDB構成確定に使用済みのため)。
- **Task3**: `known_items.md` に Rev.8 追記(background古典2件を PsycINFO 不使用の
  正当化・残余リスク点検と接続する境界文献として位置づけ)。gold set一本化・in-scope拡充メモは
  Rev.7 で対応済み。
- **Task4**: `outputs/venue_dropped_known_items.csv` / `snowballing_protocol.md` は
  **Rev.7で整備済みのため追加作業なし**。`snowballing_protocol.md` に Rev.8 追記
  (スノーボーリングが PsycINFO不使用の残余リスクを部分緩和する役割を明記)。
- `scripts/pubmed_unique_audit.py` の docstring に Rev.8 位置づけ追記(参考記録化・優先度格下げ、削除なし)。
- known_item_test.py 再実行で健全性確認(recall 69.23% 不変)。
- **次回やること(著者、優先度順)**:
  1. ACM Abstract / Scopus Keyword を再エクスポート(不可なら enrich_abstracts.py を著者実行)→ 充足率再測定
  2. `snowballing_protocol.md` に従い脱落6件を回収 → `outputs/snowballing_log.csv` 記録 → PRISMA 右カラム確定
  3. Rev.6 第2波再検索を **3DB(ACM/IEEE/Scopus)のみ**で実施 + verbatim フィールド構文記録
     → 公式再実行(PubMed除外した統合データで再構築)→ step0 recall 再測定(目標≥80%)
  4. 上記確定後に rule.md 本文へ反映(DB構成=3DB、scope=TA、Threats に PsycINFO正当化+venue取りこぼし)
  5. (優先度低・参考記録)`outputs/pubmed_unique_175.csv` の30件 judge_relevance 判定は
     PubMed不使用確定により意思決定には不要。実施は任意

### 2026-07-22 (2) — Rev.6第2波再検索(IEEE+Scopus)の自動化ツール整備
- **背景**: `docs-system/`(Semantic Scholar連携のNext.jsアプリ、作りかけ)を参考に、
  「APIを駆使して自動で再検索できるツール」を要望。ACM Digital Library には一般利用可能な
  検索APIが無いため、**IEEE Xplore + Scopus の自動化に絞る**ことを著者確認のうえ決定
  (ACMは引き続き手動エクスポート)。
- **`scripts/api_search_common.py` 新規**: Rev.6 の3コンセプト群(`CONCEPT_GROUPS_REV6`)から
  IEEE Command Search 構文(`"Document Title":`/`"Abstract":`)と Scopus `TITLE-ABS(...)` 構文を
  **単一定義から機械生成**するビルダー(`build_ieee_querytext`/`build_scopus_query`)を実装。
  手書き2DB分の表記不一致(Rev.7/8で問題化した「verbatim フィールド構文の不一致」)を構造的に防ぐ。
  加えて礼儀正しいHTTP再試行(`polite_get`)、RIS出力(`write_ris`)、実行ログ追記
  (`append_hit_log` → `outputs/api_search_log.csv`)を共通部品として実装。
- **`scripts/db_search_ieee.py` 新規**: IEEE Xplore Metadata API 検索(要 `IEEE_API_KEY`)。
  ページング・`--count-only`・年フィルタ対応。出力 `raw/ieee_wave2_YYYYMMDD.ris`。
- **`scripts/db_search_scopus.py` 新規**: Scopus Search API 検索(要 `SCOPUS_API_KEY`、
  任意で `SCOPUS_INSTTOKEN`)。5,000件超で cursor モードに自動切替。Abstract欠落率が
  高い場合は entitlement 不足の警告を表示。出力 `raw/scopus_wave2_YYYYMMDD.ris`。
- **設計判断: 出力はRIS(Zotero直接インポート用)**。既存運用(`search_replication.md` Option A)が
  Zotero経由のCSVエクスポートを前提にしているため、生CSVを直接 raw/ に置く方式(スキーマの
  厳密一致を要求され脆い)は採らず、RIS→Zotero取り込み→既存の再エクスポート手順に接続する形にした。
- **健全性確認**: 3スクリプトの構文チェック(ast.parse)、クエリビルダーの出力確認、
  RIS書き出しの整形確認、APIキー未設定時に**ネットワークに触れず**エラー終了することを確認、
  `known_item_test.py` 再実行で既存パイプラインへの影響が無いことを確認(recall 69.23% 不変)。
  **外部API通信を伴う本実行はしていない**(著者実行前提、方針どおり)。
- `docs/search_replication.md` の Option B に自動化スクリプトへの導線を追記(ACMは手動継続と明記)。
- **次回やること(著者、優先度順)**:
  1. IEEE_API_KEY(developer.ieee.org)・SCOPUS_API_KEY(dev.elsevier.com)を取得
  2. 各スクリプトを `--count-only`→少数件→本実行の順で試験(フィールド名のAPIドリフトを確認)
  3. 出力 .ris を Zotero に専用コレクション(ieee_wave2/scopus_wave2)で取り込み→CSVエクスポート
  4. `docs/search_strings.md` に verbatim クエリ・実行日・ヒット数を転記(`outputs/api_search_log.csv`が下書き)
  5. ACM は手動エクスポートを実施し、3DB分が揃ってから統合・パイプライン再実行

### 2026-07-22 (3) / 2026-07-27 — APIキー投入・接続テスト・Scopus scope実測
- **セキュリティ整備**: `.gitignore` に `.env`/`.env.*` を追加(`!.env.example`で例外)。
  実キーは `.env`(git管理外、追跡ファイルへの漏洩なしを `git check-ignore`/`git grep` で確認済み)、
  変数名テンプレートは `.env.example`(コミット可)に分離。`scripts/api_search_common.py` に
  `load_dotenv()` を追加し、`db_search_ieee.py`/`db_search_scopus.py` が自動読み込みするよう配線。
- **接続テスト(--count-only、RIS出力なし・低リスク)**:
  - **IEEE Xplore: 403 `ERR_403_DEVELOPER_INACTIVE`**。新キーに更新後も同一エラー
    → キー固有ではなく developer.ieee.org の**アカウント自体が未有効化**。著者確認待ち
    (コード側の問題ではない)。
  - **Scopus: 成功**。`TITLE-ABS`(Rev.7/8 TA方針)= **2,533件**。
- **重要な発見: Scopus scope の実測証拠**。`TITLE-ABS-KEY` でも実行し **4,727件**。
  旧初回検索の記録値(Rev.3、4,331件)は G1拡張後の TITLE-ABS(2,533)より多く矛盾する一方、
  TITLE-ABS-KEY(4,727)とは整合 → **旧検索は実際には TITLE-ABS-KEY だった可能性が高い**
  (search_strings.md の「要著者確認」に対する初の実測証拠)。
  **著者決定: TA基準は維持**(scope方針は変更しない)。ただし「TA基準は旧検索実質より-46%狭い」
  ことを Threats to Validity に明記し、Keyword経由でのみ捕捉されていた文献の残余リスクは
  スノーボーリングで緩和する対象とすることを `methodology_decision_Rev7.md` §Rev.8補足(2026-07-27)、
  `protocol_changelog.md`、`search_strings.md` に記録。
- Semantic Scholar API キーも `.env` に投入済み(`scripts/enrich_abstracts.py` で使用予定、
  未実行 — ACM Abstract 補完はまだ実施していない)。
- **次回やること(著者、優先度順)**:
  1. developer.ieee.org でアカウント有効化状況を確認(承認待ち/メール認証等)
  2. IEEE有効化後、`--count-only`→本実行(RIS出力)の順で試験
  3. Scopus は scope=TITLE-ABS(既定)で本実行(RIS出力)→ Zotero取り込み
  4. `scripts/enrich_abstracts.py` を実行して ACM Abstract 補完を試す(S2キー投入済み)
  5. rule.md 本文の Threats to Validity に Scopus scope の狭化(-46%)を明記

### 2026-07-30 — IEEE設定見直し(未解決)/ Scopus本実行 / ACM補完試験 / スノーボーリング自動化
- **IEEE**: アカウント設定を著者が見直したが、新キーでも同一の
  `ERR_403_DEVELOPER_INACTIVE` が継続。コード側の問題ではなく developer.ieee.org
  側の設定(サブスクリプション/メール認証等)の可能性。**未解決、著者確認継続**。
- **Scopus本実行(Task1)**: `scripts/db_search_scopus.py --use-default-query` を本実行し
  `raw/scopus_wave2_20260730.ris` を生成。**2,542件**(7/27の count-only 2,533件から+9、
  3日分の自然な索引増加と推定)。**Abstract充足率100%**、Keyword充足あり(旧raw/Scopus.csvの
  1.2%から大幅改善)、DOI充足率88.5%。`outputs/api_search_log.csv` に実行記録済み。
  次: Zoteroへ専用コレクション取り込み→CSVエクスポート。
- **ACM Abstract補完 少数件試験(Task2)**: `scripts/enrich_abstracts.py` に
  `SEMANTIC_SCHOLAR_API_KEY`(.envの実変数名)の読み込み漏れ・`load_dotenv()`未呼び出しの
  バグを発見・修正(旧コードは `S2_API_KEY` のみを見ており .env の値を拾えていなかった。
  後方互換で両方の変数名を受理するよう修正)。ACM Abstract欠落 **7,655件**(全件DOIあり)から
  20件を無作為抽出して試験 → **11/20(55%)成功、全件 Semantic Scholar 経由**
  (Crossref経由は0件)。個別のDOIでCrossref直接確認し、**これはバグではなく該当ACM論文に
  Crossref側のAbstractメタデータが元々存在しない**ことを確認(コード正常動作)。
  試験用一時ファイルは削除済み。**本実行(7,655件)は未実施**(著者判断待ち)。
- **スノーボーリング自動化(Task3)**: `scripts/snowball_search.py` 新規作成。
  Semantic Scholar API で前方(citations)・後方(references)引用探索を自動化
  (`docs-system/lib/semantic-scholar.ts` の getCitations/getReferences と同じAPIを使用)。
  既定シードは `outputs/venue_dropped_known_items.csv`(#)と `self_scale_references.csv`(ID)を
  結合してDOIを取得(6件、動作確認済み)。既存コーパス(raw/*.csv・raw/*.ris・
  step3_kw_included.csv、計13,069キー)との重複判定、CORE/SJRランキング参考情報の自動付与を実装。
  **PICOS採否・関連性判断は自動化しない**(picos_decision/reason列は著者記入、既存方針どおり)。
  ネットワークを使わない範囲(シード読み込み・既存キー読み込み・pipeline.pyインポート・
  argparse)は動作確認済み。**実際のAPI呼び出しは未実施**(著者実行前提)。
- **セキュリティ**: `.env` は今回も追跡対象外を確認。キーの値を出力・ログに残していない。
- **次回やること(著者、優先度順)**:
  1. developer.ieee.org でアカウント設定を再確認(サブスクリプション/メール認証等)。
     解決しない場合はIEEEサポートへの問い合わせも検討
  2. `raw/scopus_wave2_20260730.ris` を Zotero に取り込み(専用コレクション)→CSVエクスポート
     → `docs/search_strings.md` に実行記録を転記
  3. ACM Abstract本実行の可否判断(7,655件、55%成功率想定、時間がかかる長時間ジョブ)
  4. `scripts/snowball_search.py` を実行し `outputs/snowballing_log.csv` を生成
     → picos_decision/reason列を著者が記入
  5. IEEE解決後、`db_search_ieee.py` の本実行→3DB分が揃ってから統合・パイプライン再実行

### 2026-07-31 — Scopus第2波のZotero取込CSV追加 / README全面見直し(§8スノーボーリング新設) / PR #2
- **Scopus第2波データの取り込み完了(前回タスク2)**: 著者が `raw/scopus_wave2_20260730.ris` を
  Zotero の専用コレクションに取り込み、CSV エクスポートして `raw/` へ配置（当初 `additional.csv`、2026-08-01 に
  `raw/scopus_wave2_20260730.csv` へ改名）。
  実測: **2,542件 / Abstract充足率 100% / DOI 88.6% / Keyword充足あり**(旧 raw/Scopus.csv の 1.2% から大幅改善)。
  **Zotero往復の無損失性を検証**: RIS と CSV のキー集合(DOI優先・正規化タイトル代替、
  `known_item_test.py` と同一基準)が**完全一致**(共通2,519 / CSVのみ0 / RISのみ0)。
  2,542レコード中ユニーク2,519件(Scopus内部重複23件は Phase 1 で吸収)。
  **第1波5CSVに存在しない純粋な新規は 256件**。
- **README に §8「スノーボーリング(引用探索)」を新設**: `scripts/snowball_search.py` の実装を文書化
  (なぜ必要か=Venue脱落6件の回収 / 処理フロー / シード選定 / 重複判定の基準 / ランク付与 /
  出力11列 / 通信の作法)。旧§8〜10は9〜11へ繰り下げ(他文書からの章番号参照が無いことを grep で確認)。
- **README全面見直し(実装・実行ログ・docs/ との突き合わせ、+368/-75行)**。事実誤りの修正:
  - §3 DB一覧: 5DB → **Rev.8 の3DB体制**(PubMed/PsycInfo は不使用理由つき打消し表記)
  - §3 検索クエリ: 掲載されていた詳細クエリは**計画段階のもので未実行**(Rev.5)。
    実行された第1波クエリ + Rev.6第2波クエリに差し替え
  - §3 方針: **LLM不使用(Rev.2)**・人手2名 + Cohen's κ を明記
  - §5 冒頭: 入力 ResearchVR2.csv → **ResearchVR3.csv + venue_aliases.csv**
  - §5 Phase 2: 照合ロジックを実装の実行順(**Step 0 エイリアス → Step A CORE 4段 → Step B SJR 2段**)に修正
  - §5 Phase 3: キーワード別件数を pipeline_log.txt の現行値へ(`\bar\b` 137→138、
    mixed reality 60→61、patients 538→539 等)。「その他」も実数を集計
  - §7 の文字化け(`フェイルセ0000…ーフ`)・脱字(「0件のは」)、§10 の古いコマンド例(`--input ResearchVR2.csv`、
    `-X utf8` 欠落)、テーブルを壊していた正規表現内のパイプを修正
- **README に未記載だった重要事項を追加**:
  - §5 Phase 2 の**既知の順序問題**(CORE fuzzy が SJR exact より先に走る。最大の実例 PACM HCI 82件)と、
    **現行 step ファイルは 7/17 15:06 実行で 16:27 追加のエイリアス表を通していない**こと
    (pipeline_log.txt に alias 統計行が無いことで確認可能。適用後の試験値 2,917→1,831)
  - §6 に **Known-Item Test の段階別 recall**(step0 69.2% → step2 23.1%、step0で4件・step2で6件脱落)
  - §3 に **Scopus scope の狭化**(TITLE-ABS 2,533 vs TITLE-ABS-KEY 4,727)
  - §4 に `.env` / `venue_aliases.csv` / gold set の探索順(実体は `self_scale_references.csv`)
  - §10 に第2波API検索・Abstract補完・Known-Item Test の手順(CLIフラグを argparse 定義と照合)
  - 冒頭に「step ファイルは Rev.6 以前で凍結中」「docs/ と食い違う場合は docs/ 側が正」
- **PR #2 作成 → マージ済み**(ブランチ `docs/readme-audit-snowball`、2コミット)。
  データ・コードは無変更(パイプライン・stepファイル・スクリプトはいずれも触っていない)。
- ~~**保留**: `raw/additional.csv` の改名~~ → **2026-08-01 に著者承認、`raw/scopus_wave2_20260730.csv` へ改名済み**
  (`git mv` で履歴を保持。README §4 の参照も更新)。
- **次回やること(優先度順)**:
  1. **`docs/search_strings.md` の DB別記録表に「Scopus(第2波)」行を追記**(PRISMA Item #7 の穴埋め)。
     verbatim・実行日・2,542件は `outputs/api_search_log.csv` に下書きあり。**ネットワーク不要・即着手可**
  2. developer.ieee.org のアカウント有効化を確認(**全体の律速**)。解決しない場合は
     IEEEサポート問い合わせ、または**IEEEも手動エクスポートに切り替える**判断
  3. `scripts/snowball_search.py` を実行 → `outputs/snowballing_log.csv` 生成
     → picos_decision/reason を著者記入(未実行。ファイル未生成を確認済み)
  4. ACM 第2波の手動エクスポート(ACMに検索APIが無いため)→ Zotero → CSV
  5. ACM Abstract 補完の本実行可否判断(7,655件、成功率55%想定の長時間ジョブ)
  6. 3DB分が揃ったら: 正規化改修(normalization_design.md 案6+1+3+4)を適用 → **公式再実行(Rev.7)**
     → known_item_test 再測定(目標 step0 ≥ 80%)→ PRISMA 数値確定 → rule.md 本文へ Rev.8 反映

### 2026-08-01 — additional.csv の改名 / Phase 4 評価者3名の確定(Rev.9)
- **`raw/additional.csv` → `raw/scopus_wave2_20260730.csv` へ改名**(著者承認)。`git mv` で履歴保持。
  README §4 の参照も更新。第2波の ACM/IEEE 分が加わったときに取得元・波が判別できるようにするため。
- **Phase 4 の評価者を3名に確定: 著者 / Yuta Kataoka / Ryoichi WATANABE**(`protocol_changelog.md` Rev.9)。
  - **要決定(著者)**: `rule.md` Rev.2 が前提にしている **Cohen's κ は2評価者専用**で3名には使えない。
    **(a) Fleiss' κ**(全件×3名・多数決+協議、報告は素直だが工数3倍) か
    **(b) ペアワイズ Cohen's κ の平均**(各文献2名の分担方式、工数は2倍だが割当記録が必須) かを選ぶ必要がある。
  - **要決定(著者)**: Phase 3b(Title/Abstract 二重スクリーニング)も同じ3名で行うのか、従来どおり2名か。
    3名にするなら Phase 3b の一致度統計も同様に変更。
  - Rev番号は暫定。検索scope変更(TA→TAK)を先に確定するなら本項を Rev.10 に繰り下げる。
- **著者報告: ACM/IEEE の第2波手動再検索を実施 → ACM 81件 / IEEE 379件**。
  第1波(ACM 7,997 / IEEE 1,276)からの下げ幅は **ACM -99% / IEEE -70%**。
  Rev.6 は G1 を*拡張*した改訂なので、減少分はすべて scope の絞り込みで説明する必要がある。
  Scopus の -41%(TAK→TA、実測済み)と比べても **ACM の -99% は外れ値**。
  - **分析(scratchpad、リポジトリ未変更)**: in-scope known-item 13件のうち、
    **タイトルだけで3概念群が成立するのは2件のみ(#7 ACM / #11 IEEE)、残り11件は Abstract のヒットに依存**。
    ACM は Abstract 欠落 7,655件(充足率4.3%)なので、`Abstract:` 句が空振りして
    **実質タイトル検索に退化している疑い**がある(81件という数字と整合)。
    ※判定は完全一致フレーズでの近似のため、語形変化を吸収するDBでは Abstract依存件数はやや過大。
  - **切り分け手順を著者に提示済み**: ①クエリが3群それぞれ `(Title OR Abstract)` で囲まれているかの確認
    (全群をタイトルのみに要求していると2桁減る)、②ACM で `Title:(G1)` のみ / `Abstract:(G1)` のみ /
    フルクエリ の3本を投げて Abstract 索引の生死を判定。
  - **判断は Known-Item Test で行う方針**: 81件/379件をエクスポートして `raw/` に置き、
    ACM の #7/#8/#13・IEEE の #11 が捕捉できるか測る。**#7/#11 はタイトルのみで通るため、
    #8/#13 が落ちていれば Abstract 経路が死んでいる証拠**。
    その結果で TA 維持か TAK 移行かを決め、scope を変える場合はプロトコル改訂として記録する。
    現 recall が step0 69.2%(目標≥80%)で未達のため、広げる方向には合理性がある。
- **次回やること(優先度順)**:
  1. Phase 4 の一致度統計 (a)Fleiss' κ / (b)ペアワイズCohen's κ と、割当方式を著者が決定
     → `rule.md` 本文へ反映(Rev.8 の未反映分とまとめて)
  2. ACM/IEEE 第2波の結果をエクスポート → `raw/` へ配置 → Known-Item Test で TA/TAK を判定
  3. `docs/search_strings.md` に第2波の記録を転記(Scopus 分は `outputs/api_search_log.csv` に下書きあり。
     ACM/IEEE 分は verbatim クエリ・実行日・ヒット数を著者から受領)
  4. developer.ieee.org のアカウント有効化(手動検索が通っているため優先度は下がったが、
     API が使えれば再現性の記録が楽になる)
  5. `scripts/snowball_search.py` の実行 → `outputs/snowballing_log.csv` の picos_decision 記入

### 2026-08-01 (2) — Rev.9 確定(3名ペア分担) / ACM 81件は構文エラーと判明・訂正
- **評価者体制を確定(Rev.9)**: Phase 3b・Phase 4 とも **評価者3名のペア分担**
  (著者×Kataoka / 著者×WATANABE / Kataoka×WATANABE)、各文献を2名が独立評価、
  **ペアごとの Cohen's κ の平均**を報告。Fleiss' κ(全件×3名)は工数1.5倍
  (5,481判定 vs 3,654判定)に見合わないとして却下。**`rule.md` 本文に反映済み**
  (Phase 3b を書き換え、Phase 4 に「評価体制」節を新設)。
  工数目安: 1,827件×2÷3 = **約1,218件/人**(従来の2名全件方式1,827件/人より軽い)。
- **キーワードスコアの位置づけを明文化**: 著者から「Phase 3b はスコア制で数を減らす話ではなかったか」
  との確認。調査の結果、**スコア制は `rule.md`・`protocol_changelog.md` のいずれにも存在せず**、
  該当するのは `simulate_screening.py` の**タスク1B(2026-05-25 の読み取り専用シミュレーション)**で
  検討のみ・未採用だった。未採用の理由は試算値に表れている: Cat3(スケール知覚KW)ヒット率が
  **3.4%** しかなく、これは **Abstract 欠損 30.8%** の直撃で、低スコアが内容起因かデータ欠損起因かを
  区別できないため。2点未満で切ると1,457件(82%)脱落し再現率優先方針と衝突する。
  → **rule.md に「読む順序のトリアージにのみ使用可・自動除外はしない」と明記**して決着。
- **【訂正】ACM 81件は scope ではなくクエリ構文のエラーだった**。著者が Title と Abstract を
  別々に実行したところ **Title 6,012件 / Abstract 8,328件**。前セッションで立てた
  「ACM の Abstract 索引が薄く `Abstract:` 句が空振りしている疑い」は**外れ**。
  **ACM DL の検索索引には Abstract が入っている**ことが確定した(8,328件ヒット)。
  手元エクスポートの Abstract 充足率 4.3% は **Zotero 取り込み側の問題**であって検索の取りこぼしではない。
  → `enrich_abstracts.py` による補完は「エクスポートのメタデータを埋める」作業であり、
  検索の網羅性とは別問題であることが明確になった。
- **残る問題: Title/Abstract を別々に取って和集合にすると、フィールド横断の一致を取りこぼす。**
  正しい TA 検索は群ごとに `(Title:G OR Abstract:G)` を取り、それを AND する形。
  和集合は真の TA 集合の**下界**にしかならない。known-item 13件中11件が Abstract 依存で、
  かつ「G1・G3はタイトル、G2は要旨のみ」(#8)のような横断ケースが典型のため実害がある。
  → **入れ子にした単一クエリを著者に提示済み**(README §3 の Rev.6 クエリを
  `(Title:G1 OR Abstract:G1) AND (Title:G2 OR Abstract:G2) AND (Title:G3 OR Abstract:G3)` の形に展開)。
  これが通ればそれを正式クエリとする。ACM の UI が受け付けない場合は和集合で進めるが、
  **「ACM DL の検索UI制約により Title/Abstract を分けて実行・統合。フィールド横断の一致は取りこぼしうる」を
  PRISMA-S の逸脱として明記**する。
- **次回やること(優先度順)**:
  1. ACM で入れ子の単一クエリを試す → 通ればそのヒット数を採用、駄目なら和集合＋逸脱記録
  2. ACM/IEEE 第2波をエクスポート → `raw/` へ配置 → Known-Item Test で recall 実測
     (ACM #7/#8/#13・IEEE #11 の捕捉を確認。#7/#11 はタイトルのみで通るため #8/#13 が判定の要)
  3. `docs/search_strings.md` に第2波の記録を転記(Scopus は `outputs/api_search_log.csv` に下書きあり、
     ACM/IEEE は verbatim クエリ・実行日・ヒット数を著者から受領)
  4. 判定シートの様式を作成(文献ID・担当ペア・両評価者の判定・除外理由・最終判定・協議メモ)
  5. 3DB分が揃ったら統合 → 正規化改修 → 公式再実行 → PRISMA 数値確定 → rule.md へ Rev.8 分を反映

### 2026-08-03 — ACM bib の打ち切り検出 / gold set の誤りを2件発見 / 検証ツール2本を新規作成
- **著者が置いた `raw/acm_title.bib` / `raw/acm_abst.bib` は使用不可と判定し、削除した**。検査結果:

  | 検査項目 | 結果 |
  |---|---|
  | エントリ数 | 両ファイルとも **1,000ちょうど**(報告ヒット数は title 6,012 / abstract 8,328) |
  | 2ファイルの共通レコード | **1,000/1,000**(キー・並び順とも完全一致) |
  | 実際の差分 | 著者名の発音記号エンコードのみ(`Wünsche` vs `W\"{u}nsche`) |
  | 収録年 | 88% が2021年以降に偏り |

  → **(1)** 2本は同一エクスポートの文字コード違いで title/abstract の別検索になっていない、
  **(2)** ACM DL のエクスポート上限1,000件で打ち切られ母集団の12〜17%しか取れていない、
  **(3)** 打ち切りが新しい年に偏った系統的なもの。この状態で Known-Item Test を回すと
  「recall が低い」という誤った結論が出るため破棄した。
- **【前セッションの訂正の追認】ACM の Abstract 索引は健全**。81件は scope ではなく
  クエリ構文のエラーだった(Abstract 検索単独で 8,328件ヒット)。手元エクスポートの
  Abstract 充足率 4.3% は Zotero 取り込み側の問題。
- **著者決定(2026-08-02)**: ACM は**出版年でスライスして手動エクスポート**(ACM DL を
  検索源とする provenance を保つ)、クエリは **title検索と abstract検索の和集合**、既存bibは削除。
  和集合はフィールド横断の一致(G1はタイトル・G2は要旨のみ、等)を取りこぼすため
  **PRISMA-S の逸脱として明記する**ことが条件。
- **★gold set の誤りを2件発見(要著者判断)** — `export_completeness_audit.py` が
  DOI一致とタイトル一致を別々に判定したことで露見した。**どちらも現行 recall を過大評価させている**。
  - **#10 Dwarf or Giant = gold set の DOI 誤記**。gold `10.2312/egve.20171356` に対し
    コーパスは `10.2312/egve.20171353`。著者(Kim & Interrante)・年(2017)・会議(ICAT-EGVE 2017)・
    タイトルが完全一致するため**同一論文**。`self_scale_references.csv` の DOI を修正すべき
    (recall への影響なし。捕捉は正しい)。
  - **#13 Does Scaling Player Size... = 別論文を捕捉している**。gold は
    `10.1145/2617917`(2014, ACM TAP 11(3))だが、コーパスに在るのは
    `10.1145/3424636.3426908`(2020, MIG 2020, Hartman et al.)。**年・会議・著者すべて異なる**。
    gold の2014年論文は raw/ 全ファイルにも ResearchVR3.csv にも**存在しない**。
    `known_item_test.py` が**タイトル一致で拾って step0 生存と判定していた偽陽性**。
  - **影響: 真の step0 recall は 9/13(69.2%) ではなく 8/13(61.5%)**。
    step2 の脱落理由に記録されている「#13 は MIG 2020 の Venue が未照合」も**別論文についての記述**。
    → 著者判断が必要: (a) gold の #13 を2020年版に差し替えるのか、
    (b) 2014年版を正として「検索式が拾えていない」扱いにするのか。
    後者なら G1/G2/G3 のどれが外れているかの分析が必要。
  - `known_item_test.py` の照合ロジック自体にも改善余地あり(タイトル一致時に
    DOI が両方あって食い違う場合は偽陽性として警告すべき)。**未修正**。
- **`scripts/export_completeness_audit.py` 新規**(ネットワーク不要・読み取り専用)。
  打ち切り疑い(1,000/2,000件ちょうど等)・ファイル内/間の重複・期待ヒット数との突き合わせ
  (`--expect`)・**gold set 照合(HIT/SUSPECT/MISS の3値)**・年分布を検査。
  出力 `outputs/export_completeness.csv`。既存 raw/ での実測が
  `search_strings.md` 記録の DB間重複(ACM∩Scopus 142 / IEEE∩Scopus 352 / PubMed∩Scopus 606 /
  IEEE∩PubMed 39)と**完全一致**することを確認済み(キー正規化が既存監査と同一基準である証拠)。
- **`scripts/merge_raw.py` 新規**。`raw/*.csv` を連結し **`Source_DB` 列を付与**して
  統合生データを生成(既定 `ResearchVR4.csv`、重複削除は Phase 1 の責務なので行わない)。
  **PubMed は Rev.8 により既定で除外**(`--include-pubmed` で明示的に包含可)。
  検証: `--include-pubmed --dry-run` の合計が **17,224件**、第2波Scopusを引くと
  **14,682件 = ResearchVR3.csv と完全一致**。既存統合データを再現できることを確認した。
  これにより「ResearchVR3.csv がどう作られたか記録が無い」(Rev.7 で問題化)が解消する。
  また既存統合CSVに取得元DB列が無く URL/DOI からの推定に頼っていた問題
  (README §7 タスク2)も、以後は Source_DB 列で解決する。
- **ドキュメント**: `search_replication.md` §1(ACM)を全面改訂
  (失敗事例・和集合方式とその代償・年スライス手順・スライス記録表・検証コマンド)、
  共通ルール4にヒット数と実件数の突き合わせを追加。README に §4.1「データ取り込みの検証」を新設、
  §5 の既定入力の記述を修正(`DEFAULT_INPUT` は `ResearchVR2.csv` のままで、
  公式実行は `--input ResearchVR3.csv`)。
- 回帰確認: `known_item_test.py` 再実行で **recall 69.23% 不変**
  (差分は第2波Scopus改名に伴う `step0_source_dbs` のラベルのみ)。
- **次回やること(優先度順)**:
  1. **gold set #13 の扱いを著者が決定**(2020年版に差し替え / 2014年版を正として未捕捉扱い)。
     #10 の DOI 誤記(`...1356` → `...1353`)も修正する。recall の公称値が変わるため最優先
  2. ACM を年スライスで再エクスポート → `raw/acm_wave2_YYYYMMDD.csv`
     → `export_completeness_audit.py` で警告ゼロを確認
  3. IEEE(379件、上限内なので分割不要)をエクスポート → `raw/ieee_wave2_YYYYMMDD.csv`
  4. `merge_raw.py` で `ResearchVR4.csv` 生成 → `known_item_test.py` で step0 recall 実測
     → **TA 維持か TAK 移行かを判断**
  5. `docs/search_strings.md` に第2波の verbatim・実行日・ヒット数・スライス内訳を転記
  6. 和集合方式の逸脱を `protocol_changelog.md` に記録(Rev.10 候補)

### 2026-08-03 (2) — ACM第2波(raw/acm2)のスライス検査 / gold set 2件を修正
- **著者が ACM 第2波を `raw/acm2/` に格納**(`acm (1).bib` 〜 `acm (19).bib`、計19本)。
  ファイル名に年・検索種別が入っていないため中身から系列を判別した。
  **ファイル番号 1-9 = title検索、10-19 = abstract検索**と判明(合計件数が報告値と対応)。

  | 系列 | ファイル | 合計 | 報告ヒット数 | 判定 |
  |---|---|---|---|---|
  | A(title) | acm (1)〜(9) | **6,013** | 6,012 | ✅ ほぼ一致・年の抜けなし |
  | B(abstract) | acm (10)〜(19) | **6,611** | 8,328 | ❌ **1,717件不足** |

- **★系列B に再取得が必要な箇所を特定**:
  1. **2005〜2009年**: スライス自体が存在しない((19)が1973-2004、(18)が2010-2015で間が空く)。推定約640件
  2. **2019年・2020年**: スライス自体が存在しない((17)が2016-2018、(15)が2021-2022で間が空く)。推定約940件
  3. **`acm (17).bib`(2016-2018)が1,000件ちょうどで打ち切り**。年分割して取り直しが必要。推定約110件
  - 推定合計 **約1,690件**で不足分1,717件とほぼ一致 → **この3つで全て説明がつく**(他に見落としなし)。
  - 推定根拠は同一年の abstract/title 比 1.15〜1.51(平均約1.35)。系列Aの該当年は
    2005-2009が472件、2019+2020が694件、2016-2018が820件。
- **抜けではないもの(確認済み)**: **1974〜1988年が0件なのは正常**((19)の1973-2004スライスが
  当該範囲をカバーしたうえで該当論文が無い。1973年に1件のみ)。系列Aに1988年以前のスライスが
  無いが、系列Bの実測から当該範囲はほぼ0件と見込まれる(念のため確認するなら「≤1988」1回で済む)。
- **`acm (16).bib` は `acm (15).bib` とバイト単位で完全同一**(同じエクスポートの二重保存)。
  重複削除で吸収されるが紛らわしいので削除推奨。
- 現状の全19ファイル合算 13,140件 / 重複除去後 **8,856件ユニーク** / Abstract 保持率 **97.6%**。

#### ★gold set 2件を修正(著者承認済み)
- **#10 Dwarf or Giant**: DOI `10.2312/egve.20171356` → **`10.2312/egve.20171353`**(誤記の訂正)。
- **#13 Does Scaling Player Size...**: DOI `10.1145/2617917` → **`10.1145/3424636.3426908`**、
  年 2014→**2020**、掲載 ACM TAP 11(3)→**MIG 2020**、VenueType Journal→**Conference**、
  著者 Piryankova ら→**Hartman, Delahaye, Decroix, Herbelin, Boulic**。
- **【前セッションの報告を訂正】真の step0 recall は 61.5% ではなく 69.23% のままで正しい。**
  前回は「gold の2014年版が実在してコーパスに無い」と解釈したが、ACM第2波の全データで確認した結果
  **その2014年版は存在しなかった**。DOI `10.1145/2617917` は実在するが
  「Olfactory Adaptation in Virtual Environments」(ACM TAP 2014)という別論文のもの。
  「Does Scaling Player Size Skew...」というタイトルの論文は ACM DL 全体で
  **2020年の MIG 論文ただ1本**であり、コーパスが捕捉していたものが正しい対象だった。
- **注意(残存する不整合)**: #13 の旧「著者」欄(Piryankova, de la Rosa, Kloos, Bülthoff, Mohler)は
  Hartman らとは別人で、Piryankova らの *Displays* 2013 論文
  「Egocentric distance perception in large screen immersive displays」の著者リストと一致する。
  旧「掲載誌+年」(ACM TAP 11(3), 2014)は Piryankova らの別論文
  「Can I Recognize My Body's Weight?」(DOI 10.1145/2641568、コーパスに在り)と一致する。
  つまり旧 #13 は**3論文の情報が混在**していた。Title・Section(IV. 自己スケールの錯誤)・
  Role_in_Survey(スケーリングが物体サイズ評価に与える歪み)・InterventionModality(Visual-Global)・
  EvaluationTarget(World-scale)がいずれも Hartman 2020 と整合するため Hartman 2020 に確定したが、
  **もし意図が Piryankova 論文だった場合は差し替えが必要**(著者確認事項)。
- 修正後の検証: `export_completeness_audit.py` の gold set 照合が
  **SUSPECT 0 / HIT 9/13(69.2%)** となり、`known_item_test.py` の値と一致。
  #10・#13 とも照合方法が TITLE → **DOI** に変わった(偽陽性の解消)。
- **PR #3(オープン中)の本文を訂正**。初版に書いた「真の recall は 61.5%」を撤回し、
  gold set の誤りが**発見**から**修正済み**に変わった旨とその根拠に差し替えた。
  タイトルも「gold set の誤りを2件修正」に更新。撤回した記述は削除せず、
  なぜ誤ったか(存在しない2014年版を想定していた)を残している。
- 本セッションのコミット: `bf46ccd`(gold set 修正・recall 訂正の撤回)。
  作業ツリーは `raw/acm2/`(未追跡・再取得待ちのため未コミット)を除きクリーン。
- **次回やること(優先度順)**:
  1. 系列B の3箇所(2005-2009 / 2019 / 2020 / (17)の年分割)を再エクスポート
  2. `acm (16).bib` を削除
  3. 全ファイルを Zotero の `acm_wave2` コレクションへ取り込み → CSV → `raw/acm_wave2_YYYYMMDD.csv`
  4. `export_completeness_audit.py --expect acm_wave2=8328` で警告ゼロを確認
  5. IEEE(379件)をエクスポート → `merge_raw.py` で `ResearchVR4.csv` → recall 実測 → TA/TAK 判断

### 2026-08-03 (3) — ACM第2波が完成(9,630件)/ スライスbibはignore、内訳は文書に記録
- **ACM 第2波の取得が完了**。著者が年スライスで再エクスポートし、不足分を3回にわたって補填。
  最終的に **title 6,013件 / abstract 8,331件 / 和集合ユニーク 9,630件**。
  UI表示値(6,012 / 8,328)をわずかに上回るが、エクスポートが数日にまたがったことによる
  索引の自然増であり不足ではない。
- **補填の経緯(打ち切り・上書き事故を含む)**:
  - 初回の23本中、系列B(abstract)に **2005-2009 / 2019 / 2020 のスライス欠落**と
    `acm (17)` の1,000件打ち切りがあり、1,717件不足していた。
  - 補填の途中で **`acm (19).bib`(1973-2004、505件)が2016年のエクスポートで上書きされ消失**。
    系列Bの2004年以前が丸ごと欠落したのを件数の突き合わせで検出し、再取得してもらった
    (8,239 → 7,759 の減少として現れた)。
  - 取り直しによる回収実績: 2016 +25 / 2017 +35 / 2018 +38 / 2019 +41 / 2020 +25。
    **打ち切り版をそのまま使っていたら計164件を取りこぼしていた。**
  - 重複ファイル7本((16)(19)(23)(24)(28) 等)を削除。**削除によるレコード損失はゼロ**を
    キー集合の比較で確認済み。
- **`scripts/merge_bib.py` 新規**。年スライスの .bib を**引用キー(=DOI)単位で一意化**して1本に統合する。
  エントリ本文は一切加工しない。ACM の年スライス運用は今後も繰り返すため再実行可能にした。
  統合結果 9,630件。事前集計の9,634件との差4件は、**同じ論文が `doi` フィールドの有無違いで
  2回入っていた**ケースで、引用キーで見れば同一。レコード損失ではないことを検証済み。
- **Zotero 取り込み → CSV は無損失**: `raw/acm_wave2_20260803.csv` は **9,630件で統合bibと完全一致**、
  ファイル内重複0、DOI充足 95.5%、Abstract充足 **97.6%**、gold set の ACM 3件は **HIT 3 / SUSPECT 0 / MISS 0**。
  第2波Scopusに続き2例目の無損失往復。
- 命名規約に合わせ `raw/acm2.csv` → **`raw/acm_wave2_20260803.csv`** にリネーム。
  `merge_raw.py` の `Source_DB` 判定が第1波 `acm.csv` と同じ "ACM" に落ちるのを防ぐため
  (リネーム後は "ACM(wave2)" として正しく分離されることを dry-run で確認)。
- **著者判断: スライス .bib はコミットせず ignore**。`.gitignore` に `raw/*.bib` と `raw/acm2/` を追加。
  **その代わり、スライス別の年範囲・件数を `docs/search_strings.md` に表として記録**した
  (PRISMA Item #7 の根拠は今後この表が正)。あわせて第2波の verbatim・実行日・ヒット数、
  和集合方式の代償(フィールド横断の取りこぼし)も同ファイルに記載。
- 統合見込み(`merge_raw.py --dry-run`): ACM 7,997 / ACM(wave2) 9,630 / IEEE 1,276 /
  IEEE(update) 297 / Scopus 4,331 / Scopus(wave2) 2,542 = **26,073件**(DB間重複含む)。
- **次回やること(優先度順)**:
  1. **IEEE 第2波(379件)のエクスポート** — 上限2,000件に収まるので分割不要。
     `raw/ieee_wave2_YYYYMMDD.csv` に配置。**これが最後の未取得データ**
  2. `merge_raw.py` で `ResearchVR4.csv` 生成 → `known_item_test.py` で step0 recall 実測
     → **TA 維持か TAK 移行かを判断**
  3. 和集合方式の逸脱を `protocol_changelog.md` に記録(Rev.10 候補)
  4. 正規化改修 → 公式再実行 → PRISMA 数値確定 → rule.md へ Rev.8 分を反映

### 2026-08-04 — 進捗ログの常設セクションを現状に更新（PR #3 マージ後）
- **PR #3 をマージ**（8コミット）。本文に ACM 第2波の節を追記してからマージした。
- **本ログの常設セクション（タイムライン / 完了していること / まだやっていないこと）を全面刷新**。
  2026-05-25 時点（ResearchVR2.csv・1,784件）の記述のまま放置されており、
  Rev.2〜Rev.9 の確定事項も第2波データも反映されていなかった。
  - **タイムライン**: Rev.2〜Rev.9 と第2波取得までの12行に更新
  - **完了していること**: 「プロトコル（Rev.9まで確定）/ 検索データ（波・DB別の表）/
    スクリーニング Phase 1〜3（凍結中である旨を明記）/ 検証基盤 / API検索の自動化 /
    関連ツール」の6区分に再編
  - **まだやっていないこと**: 優先度順に A.データ取得（残りIEEEのみ）/ B.統合と再実行 /
    C.スクリーニング本体 / D.補助タスク の4群・17項目へ再編
- **既知の課題に4件追加**（今回の作業で得た教訓）:
  1. **DBエクスポートは黙って打ち切られる**（ACM 1,000 / IEEE 2,000）。打ち切りは新しい年に偏るため
     recall を誤らせる。対策は年スライスと UI表示件数との突き合わせ
  2. **ACM の和集合方式はフィールド横断の一致を取りこぼす** → PRISMA-S に逸脱として明記が必要
  3. **gold set のメタデータ品質** — #10/#13 で誤りが見つかった。他項目にも残存の可能性
  4. **`known_item_test.py` はタイトル一致の偽陽性を検出できない**（本体は未修正）
- **現在地の要約**: プロトコルは Rev.9 まで確定。第2波データは Scopus(2,542) と ACM(9,630) が取得済みで、
  **残るは IEEE の379件のみ**。それが揃えば `ResearchVR4.csv` → recall 実測 → TA/TAK 判断 →
  正規化改修 → 公式再実行 → PRISMA 数値確定、と一本道で進める。
- **次回やること**: 上記「まだやっていないこと」§A の1項目（IEEE エクスポート）から。
