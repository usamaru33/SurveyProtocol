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
| 2026-08-10 | **IEEE 第2波（361件）を取得 → `ResearchVR4.csv`（26,434件）生成**。Rev.10: 検索scope を TA に確定、スノーボーリングの目的分離 |
| 2026-08-11 | Rev.11: 全文書監査。gold #3 を background へ、Rev.10 の根拠数値を訂正 |
| 2026-08-12 | **Rev.12: Venue正規化の構造ガード + 公式再実行（凍結解除）**。Rev.13: フィルタ層（Phase 1.5）新設。Phase 3b の判定シート基盤を整備 |
| 2026-08-15 | **Rev.14: gold set を17件へ拡充**（卒論の参考文献より）。略称照合の修正 |
| 2026-08-16 | **Rev.15: スノーボーリング実行 → Phase 3b の判定対象 1,052件で確定** |
| 2026-08-17 | **Rev.16: 要旨を外部補完**（欠落 325→191件）。**Rev.17: Phase 3b を liberal accelerated へ変更**。配布可能な状態に到達 |
| 2026-08-19 | **Rev.18: 除外理由を統制語彙（9択）に**。**Rev.19: 判定シートを配布し設計を凍結**。評価者向け説明資料を作成 |
| 2026-08-20 | **Rev.20: 語彙と Rev.14 の S基準運用の矛盾を、語彙を変えず解釈の明示で解消**。事前配布資料を作成・PDF組版。説明会（評価者2名） |

---

## 完了していること

### 1. プロトコル（Rev.20 まで確定）
- **DB構成: 3DB（ACM DL / IEEE Xplore / Scopus）**。PubMed は Rev.8 で不使用に確定、PsycINFO はアクセス制約で不使用。
- **判定に AI/LLM は不使用**（Rev.2）。Phase 3a は決定論的キーワード除外、Phase 3b/4 は人手。
- **Venue 基準: CORE A*/A のみ + SJR Q1 のみ**（Rev.4）。Q2脱落826件は Threats で報告。
- **検索 scope: TA（Title-Abstract）**（Rev.10 で最終確定）。第1波のみ scope が異なる（Scopus=TAK / IEEE=広域、Rev.11）。
- **Phase 3b は liberal accelerated**（Rev.17）: 1名の Include で通す / Exclude には2名。
  κ は3名全員が判定する校正セット164件で算出。Phase 4 は通常の二重評価（Rev.9 の体制）。
- **Phase 3b は 2026-08-19 のシート配布をもって凍結**（Rev.19）。シート再生成・判定手法・
  除外理由の語彙・割当は変更しない。`make_screening_xlsx.py --force` と `pipeline.py` の再実行は禁止。
- **`S: 原著論文でない` の解釈**（Rev.20）: 実験を報告していない文献種別を指す。
  **実験を報告しているポスター/ショートペーパーは Include**。ページ数は除外理由にしない。
  **語彙の文言は配布時のまま変更していない**（→ 既知の課題・Threats）。
- 変更履歴は `docs/log/protocol_changelog.md`。**`rule.md` 本文は Rev.11 までを反映済み（2026-08-11）。**

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

- 第2波は Rev.6 の G1拡張クエリ。ACM は **title検索 6,013 + abstract検索 8,331 の和集合**（`docs/protocol/search_strings.md` にスライス内訳）。
- Zotero 往復の無損失を3例で実測（Scopus 2,542 / ACM 9,630 / IEEE 361 とも一致）。
- **統合生データ `ResearchVR4.csv` = 26,434件**（`scripts/merge_raw.py`、Source_DB 列つき、PubMed 除外）。

### 3. スクリーニング Phase 1〜3（**Rev.12 公式再実行済み・凍結解除**）

```
26,434 件（ResearchVR4.csv = 3DB × 第1波+第2波）
  → Phase 1   重複削除        : -8,092  → 18,342 件（+ 重複コピーからのフィールドマージ）
  → Phase 1.5 フィルタ層      : -12,025 →  6,317 件（pass 2,610 / hold 3,707）
  → Phase 2   Venueランク      : -5,138  →  1,179 件
  → Phase 3a  キーワード除外    : -384    →    795 件（step3_kw_included.csv ★最終候補）
```

- **2026-08-12 に正規化改修（Rev.12）を適用して公式再実行**。2026-07-17 15:06 以来の凍結を解除した。
  旧値（14,682→12,543→2,909→1,827）は第1波・4DB 前提であり**以後は使用しない**。
- Phase 3a 内訳: Cat1 非没入 112 / Cat2 技術・非実証 24 / Cat3 臨床・医療 262。
- **Phase 1.5 フィルタ層（Rev.13）**: 取得後に正規化クエリを一律再適用し、DB間の検索scope差を吸収する。
  要旨が無いレコードは判定不能として `hold`（除外せず人手へ）。gold set の脱落は 0 件。
- Phase 1 で重複コピーから **Abstract 4,172件 / ISSN 1,474件** を補完（外部API不要）。
- Phase 2 出力に `Match_Stage` / `Match_Guard_Note` を追加（誤照合を可視化する監査列）。
  unmatched 9,066件のうちガード起因は 865件（9.5%）。
- **Phase 3b の判定対象は 1,052件**（DB検索795 + 引用探索257）。liberal accelerated により
  著者1,052件 / 他2名は校正セット164件 + 著者の Exclude/Unsure 分担（割当上限 Kataoka 449 / WATANABE 439。
  実数は著者の stage 1 完了時に確定）。
  引用探索分には venue フィルタとフィルタ層を適用していない（`snowballing_protocol.md` §4.3b）。

### 3b. Phase 3b の実施基盤（**配布可能な状態**）
- 判定対象 **1,052件**（DB検索795 + 引用探索257）。**liberal accelerated 方式**（Rev.17）:
  1名の Include で通す / Exclude には2名。stage 1 は著者1,052件 + 他2名が校正セット164件、
  stage 2 で著者の Exclude/Unsure 分を2名が分担（割当上限 Kataoka 449 / WATANABE 439）。
- `screening/` に判定シート一式（CSV + xlsx、`source` 列つき）。
  評価者ごとに独立したファイル（互いの判定が見えると κ が意味を失うため）。
  ブロック割当は決定論的（キーの MD5 mod 3）で、再生成しても既存の割当は動かない。
- `scripts/make_screening_sheets.py`（生成）/ `make_screening_xlsx.py`（Excel版）/
  `score_screening.py`（ペア別 Cohen's κ・協議リスト・最終判定）。
- 運用手順は `docs/protocol/screening_protocol.md`。
- **着手前の未決事項**: 要旨欠落 **325件（30.9%）** の扱い（補完するか、欠落のまま Threats に明記するか）。

### 4. 検証基盤
- **Known-Item Test**（`scripts/known_item_test.py`）: gold set = `self_scale_references.csv`（in-scope 17件、卒論の参考文献から5件を拡充）。
  現在 step0 **76.47%**（13/17、目標 ≥80%）→ step1.5 64.71% → step2 **29.41%**（Rev.14）。
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
- `scripts/snowball_search.py`（S2 引用探索、**Rev.15 で再実行済み** 475行/新規317件→判定対象257件）、`scripts/enrich_abstracts.py`（Abstract補完、少数件試験のみ）。

### 6. 関連ツール `../docs-system`（Next.js、別リポジトリ相当）
- Semantic Scholar 検索 → 引用ネットワーク可視化（D3）→ Supabase + R2。**サーベイ本体とは未接続。**
  `../DocsSystem` は空フォルダ（廃棄した試作跡）。

---

## まだやっていないこと（優先度順）

### A. データ取得 — ~~完了~~
1. ~~IEEE 第2波のエクスポート~~ → **完了（2026-08-10、361件）**。
   3DB × 第1波+第2波が揃い `ResearchVR4.csv`（26,434件）を生成済み。
   IEEE API は `ERR_403_DEVELOPER_INACTIVE` のままだが、手動エクスポートで代替したため**律速ではない**。

### B. 統合と再実行 — ~~完了~~
2. ~~recall 実測 → TA/TAK 判断~~ → **TA 維持で確定（Rev.10、根拠は Rev.11 で訂正）**
3. ~~Venue 正規化の改修~~ → **適用済み（Rev.12）**。略称照合の向きは Rev.14 で追加修正
4. ~~公式再実行~~ → **完了（Rev.12〜15）**。2026-07-17 以来の凍結を解除
5. ~~`rule.md` へ Rev.8 分を反映~~ → **反映済み**（Rev.11 で3DB構成、Rev.13 で Phase 1.5、
   Rev.15 で venue 制限の位置づけ）
6. ~~和集合方式の逸脱を記録~~ → **記録済み（Rev.11）**

### C. スクリーニング本体
7. **Phase 3b: Title/Abstract スクリーニング** — **liberal accelerated**（Rev.17）。
   1名の Include で通す / Exclude には2名。κ は3名全員が判定する校正セット164件で算出
   （除外プールだけでは κ が常に 0 になるため）。
   - ~~判定シート様式が**未作成**~~ → **作成済み（2026-08-12）**。
     `scripts/make_screening_sheets.py`（生成）/ `scripts/score_screening.py`（κ算出・協議リスト）/
     `docs/protocol/screening_protocol.md`（運用手順）。**評価者ごとに別ファイル**にして独立性を担保。
     ブロック割当は決定論的（キーの MD5 mod 3）。**Excel版（.xlsx）も生成済みで記入待ち**
     （ブロック1 325件 / 2 356件 / 3 371件）
   - キーワードスコアは読む順序のトリアージにのみ使用可。自動除外はしない
   - **⚠️ 着手前に決めること: 要旨欠落 325件（30.9%）の扱い**（左170 + 右155）。
     Rev.13 の重複マージで左カラムは大幅に回収したが、引用探索側は Crossref の参考文献リストが
     DOI しか返さないため欠落率60%。この文献は**タイトルのみでの判定**になる。
     `enrich_abstracts.py` で補完（S2経由・成功率約55%の長時間ジョブ）してから配布するか、
     欠落のまま配って Threats に明記するか。**後から補完すると判定のやり直しになる**
8. **Phase 4: 全文適格性評価** — PICOS基準。体制は Phase 3b と同一。
   **除外理由（PICOS のどの基準に抵触したか）を1件ずつ記録**すること
9. **Taxonomy コーディング** — 採択文献への3軸分類の付与
10. **分析・考察** — 年代×Taxonomy変遷、Venue別トレンド、タスク×モダリティ、非視覚パラメータ体系化
11. **PRISMA フロー図の作成**、`rule.md` 冒頭の「○○件」の確定値への置換

### D. 補助タスク（並行可能）
12. ~~**スノーボーリング実行**~~ → **実行済み（Rev.15、2026-08-16）**。475行→新規317件→
    判定対象257件。判定は Phase 3b の判定シートに統合したため `picos_decision` 列は未使用。
    残: タイトル取得不能3件の手作業同定（`snowballing_protocol.md` §4.4）
13. **Venue suspect の目視確認** — 優先度P1 = 91ユニーク/240件（`outputs/venue_suspect_matches.csv`）
14. ~~**gold set の in-scope 拡充**~~ → **17件に到達（Rev.14、卒論の参考文献から5件追加）**。
    目標15〜25件の範囲内。ただし**コーパスに不在の境界事例**（例: Ogawa et al. 2014 IEEE VR
    「Changing the perceived size of a virtual object by modifying its motion velocity」）の
    追加は継続課題。拾えた文献だけを gold にすると recall が構造的に高く出る（循環）ため
15. **ACM Abstract 補完の要否判断** — 検索の網羅性とは別問題と判明したため優先度は低いが、
    Phase 3b で人が要旨を読む以上は必要（第2波ACMは97.6%充足なので対象は第1波分）
16. **引用数の補完** — S2 API で citationCount 取得。**専用スクリプトは未整備**。
    採用にはプロトコル改訂が必要
17. ~~`known_item_test.py` の照合ロジック改善~~ → **実装済み（Rev.12）**。両方向の偽陽性を検出
    （タイトル一致だがDOI不一致 / DOI一致だがタイトルが別物）。導入と同時に gold #6 の
    タイトル誤記を検出。Rev.14 で step1_5 の段追加と誤植許容（0.95）も入れた
18. **レビュー/サーベイ論文の除外** — 最終795件中に25件残存。S基準（実証研究）での除外は
    Phase 3a のパターン強化で機械的に対応可能（未実施。目標件数を既に下回っているため保留中）

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
- **除外理由の語彙と運用解釈に齟齬がある（Rev.20、Threats 必須）** — Rev.18 の統制語彙
  `S: 原著論文でない` の定義に「ポスター」が入っているが、実際の運用は Rev.14 の
  「実験を報告していれば2ページのポスター/ショートペーパーも含める」。
  **語彙の文言は配布時のまま変更していない**（Rev.19 の凍結維持）ので、
  **公開する語彙表と運用解釈が一字一句同じではない。** Threats to Validity に
  ①齟齬があったこと ②判定開始前（2026-08-20、記入0件時点）に全評価者へ同時に補足したこと
  ③文言は変更していないこと ④最終コーパスに2ページ論文が含まれることと件数、の4点を書く。
  **stage 2 のシート生成時も同じ補足を書面で添えること**（stage2 の「はじめに」にも同じ語彙が再掲される）。
- **gold set 17件のうち8件が stage 2 で評価者に配られる** — `reviewer_briefing.md` §2.1 は
  17件を「確実に対象」として表に出しているが、うち8件は 888件側にあり
  stage 2 の担当が確定済み（kataoka 4 / watanabe 4）。**κ は校正セット164件でのみ算出するので
  κ への影響は無い**が、stage 2 の独立性の前提は緩む。表を9件に絞るか Threats に記録するかは判断待ち。
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
- `docs/protocol/search_replication.md` の Option B に自動化スクリプトへの導線を追記(ACMは手動継続と明記)。
- **次回やること(著者、優先度順)**:
  1. IEEE_API_KEY(developer.ieee.org)・SCOPUS_API_KEY(dev.elsevier.com)を取得
  2. 各スクリプトを `--count-only`→少数件→本実行の順で試験(フィールド名のAPIドリフトを確認)
  3. 出力 .ris を Zotero に専用コレクション(ieee_wave2/scopus_wave2)で取り込み→CSVエクスポート
  4. `docs/protocol/search_strings.md` に verbatim クエリ・実行日・ヒット数を転記(`outputs/api_search_log.csv`が下書き)
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
     → `docs/protocol/search_strings.md` に実行記録を転記
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
  1. **`docs/protocol/search_strings.md` の DB別記録表に「Scopus(第2波)」行を追記**(PRISMA Item #7 の穴埋め)。
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
  3. `docs/protocol/search_strings.md` に第2波の記録を転記(Scopus 分は `outputs/api_search_log.csv` に下書きあり。
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
  3. `docs/protocol/search_strings.md` に第2波の記録を転記(Scopus は `outputs/api_search_log.csv` に下書きあり、
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
  5. `docs/protocol/search_strings.md` に第2波の verbatim・実行日・ヒット数・スライス内訳を転記
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
  **その代わり、スライス別の年範囲・件数を `docs/protocol/search_strings.md` に表として記録**した
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

### 2026-08-10〜16 — Rev.10〜15: 凍結解除から Phase 3b 着手可能まで

2026-07-17 以来凍結していた step ファイルを解除し、**人手スクリーニングを始められる状態**
（判定対象1,052件・シート配布可能）まで到達した。プロトコル改訂6本を含む。各改訂の詳細は
`docs/log/protocol_changelog.md` にあるので、ここでは**なぜそうしたか**を中心に記録する。

#### 確定した数値

```
26,434 → 18,342（P1 重複削除）→ 6,317（P1.5 フィルタ層）→ 1,179（P2 Venue）→ 795（P3a）
                                                          + 引用探索 257（右カラム）
                                                          = Phase 3b 対象 1,052 件
```

Known-Item Test: step0 **13/17（76.47%）** → step1.5 64.71% → step2 29.41%。

#### 判断の骨子（意図）

**1. TA scope の確定（Rev.10）— 工数と recall のトレードオフ**
第2波12,533件が gold を1件も新規回収しなかった一方、TAK は Scopus 実測で +87%。
人手2名/件の工数をほぼ倍にする対価に見合わないと判断した。**Rev.11 で根拠を訂正**:
当初「TA だと recall 61.5%」としたが、これは gold #3 を分母に含めた場合の値で、
除いた再計算では全体・第1波・第2波が同値だった。**TA 確定に recall コストは無かった**。

**2. Venue 正規化の構造ガード（Rev.12）— 「照合漏れ」と「ランク不足」を分ける**
最大の誤照合（PACM HCI 78件）を解消。**質的に重要なのは数値ではなく脱落の性質**で、
venue 脱落 known-item の内訳が「照合漏れ3」→「照合漏れ1／ランク不足3」に変わった。
Threats の主張が「照合の不具合＝直すべき欠陥」から「品質基準そのものの帰結＝設計判断」に変わる。

**3. フィルタ層の新設（Rev.13）— 件数削減ではなく DB 差の吸収**
Phase 3b の対象が2,659件と過大だったのが発端だが、採ったのは
「キーワードスコアで足切り」ではなく **Rev.7 で承認済み・未実装だった方針3の実装**。
スコア足切りは gold 12件中3件（Being Barbie 含む）を落とし、しかも要旨欠落と交絡して
「メタデータが欠けているから除外」になる。フィルタ層は
**「DBごとに検索の当たり方が違うので取得後に同じクエリを一律再適用する」**という
説明で済み、閾値の恣意性を弁明せずに済む。
**配置は著者の指摘で修正**した（選定基準の後→前へ）。「取得の差を均す処理」と
「適格性で落とす処理」は性格が違うので段を分ける。この移動の過程で
**Phase 1 が要旨を捨てていた**ことも判明し、Abstract 4,172件を外部API不要で回収した。

**4. gold set の拡充（Rev.14）— 卒論の参考文献から5件**
「引用予定リストから逆算して選ぶ」という選定ガイドラインに合致する出典。
聴覚（#21 Sikström）と触覚（#24 Okada）が in-scope に1件も無かった穴を埋めた。
**拡充が2つの実害を暴いた**: 略称照合のサニティチェックが IEEE VR を棄却していたこと（27件）と、
フィルタ層が gold 2件を落とすこと。後者について3案を実測比較し、
**語彙追加は G2 に `user` を入れることになり概念群の定義を壊す**ため
3群必須を維持し、Threats で報告する立場を採った。

**5. スノーボーリング実行と右カラムの適用範囲（Rev.15）**
判定対象を確定させてから配布する方が確実、という判断で実行。
**右カラムに何を適用するかは実測で決めた**: venue フィルタを適用すると165件が消えるが、
その83%は品質判断ではなく照合失敗（右カラムの venue 文字列は Crossref/S2 由来で非正規）。
`Science`・`Cognition` が未照合で落ち、回収対象そのものである `Presence`・`ICAT-EGVE` も落ちる。

#### ⚠️ 前例が確認できなかった判断（報告義務あり）

**「DB検索には venue フィルタを適用し、引用探索には適用しない」という非対称**について、
PRISMA 2020 公式フロー図・Wohlin 2014・DB検索とスノーボーリング併用の研究を調べたが、
**明確な前例は見つからなかった**。適格性基準は経路によらず一律適用が原則とされている。

成立の前提は「**venue 制限は検索スコープの定義であって適格性基準ではない**」という位置づけで、
`rule.md` §Phase 2 に明記した。**本文で「採択文献が2つの異なる品質レジームから来る」ことを
明示する義務がある**（「A*/A・Q1のみ」と書きながら Presence 誌の論文が入っていれば矛盾に見える）。

逆方向の逸脱も併記した: PRISMA は右カラムを全文評価へ直行させるが、本レビューの右カラムは
機械生成なので Title/Abstract 段を設ける（**規定より慎重**な方向なので説明は容易）。

#### 途中で見つけて直した不具合

1. **`merge_bib.py` のサイレント欠落** — IEEE の bib はエントリが改行なしで直結されるため、
   `^@` 行頭アンカーでは1ファイル1件しか認識せず370件中365件を警告なしに捨てていた
2. **Phase 1 が要旨を捨てていた** — 重複削除が先出優先で、ACM（要旨なし）が Scopus（要旨あり）より
   先に並んでいるだけの理由で要旨を捨てていた
3. **Venue名をマージしたら照合が壊れた** — gold #11 の venue が IEEE 表記から Scopus 表記に
   置き換わり step2 recall が 3/12 → 2/12 に低下。Venue はマージ対象から除外した
4. **`known_item_test.py` の偽陽性** — DOI が食い違ってもタイトルが一致すれば「捕捉」と判定していた
   （gold #13 の誤りを見逃した原因）。両方向の検出を実装し、導入と同時に **#6 のタイトル誤記**を検出
5. **サニティチェックの過剰棄却** — 元文字列類似度だけでは定型句で薄まった venue 名が
   正しい照合先に対しても0.5程度しか出ず、正当な照合まで棄却していた
6. **略称照合の向きが逆** — `2015 IEEE virtual reality (VR)` が CORE A* に当たっているのに棄却。
   略称ではデータ側が公式名より短いのが普通なので、包含の向きを逆にする必要があった
7. **Known-Item Test の脱落段の誤帰属** — `STEPS` に step1_5 が無く、フィルタ層で落ちた文献が
   「step2 で脱落」と報告されていた。脱落段の帰属は Threats の記述に直結する

#### 卒論（`GradThesis_Maeno_2025.pdf`）の参考文献に誤り2件

論文を書く際に修正が必要。
- **[7]** は「Piryankova ら / ACM TAP 11(3) / 2014」だが、当該タイトルの論文は
  **Hartman ら / MIG 2020** の1本のみ。**これが gold set #13 の誤り（3論文混在）の発生源**
- **[11]** と **[33]** が同一タイトルで別著者。実在は **[33] Pouke 2020** のみ

#### 成果物

- `screening/` に判定シート一式（CSV + xlsx、`source` 列つき）。著者681 / Kataoka 696 / WATANABE 727
- `scripts/`: `make_screening_sheets.py` / `make_screening_xlsx.py` / `score_screening.py` を新設
- `docs/protocol/screening_protocol.md` を新設（Phase 3b の運用手順）

#### 次回やること（優先度順）

1. **要旨欠落325件（30.9%）の扱いを決める** — 左170 + 右155。この文献はタイトルのみでの判定になる。
   `enrich_abstracts.py` で補完（S2経由・成功率約55%の長時間ジョブ）してから配布するか、
   欠落のまま配って Threats に明記するか。**配布前に決めること**（後から補完すると判定のやり直しになる）
2. **判定シートの配布** → Phase 3b 開始
3. タイトル取得不能3件の手作業同定（`snowballing_protocol.md` §4.4）
4. gold set の境界事例の追加（コーパス不在の文献。例: Ogawa et al. 2014 IEEE VR）
5. 最終784→795件にレビュー/サーベイ論文が25件残存。S基準での除外は Phase 3a のパターン強化で対応可能

### 2026-08-17 — Rev.16: 要旨の外部補完（欠落 325 → 191件）

判定シート配布前の最後の懸案だった「要旨欠落325件（30.9%）の扱い」を解決した。

#### やったこと

DOI を持つ280件に Crossref / Semantic Scholar を照会し、**134件（48%）で要旨を取得**。
要旨欠落は **325件（30.9%）→ 191件（18.2%）** に改善した。

| 取得経路 | 件数 | 元からあり | 補完 | 無し |
|---|---|---|---|---|
| DB検索 | 795 | 625 | 107 | 63 |
| 引用探索 | 257 | 102 | 27 | 128 |
| **合計** | **1,052** | 727 | **134** | **191** |

#### 判断の骨子（意図）

**当初は「上流で補完してパイプラインを再実行する」案を推したが、先行研究を確認して撤回した。**

再実行すると、補完した要旨で Phase 1.5（フィルタ層）と Phase 3a（キーワード除外）が
**追加で発動**する。これは PRISMA 2020 の構造と衝突する。公式フロー図は自動ツールによる除外を
"Records marked as ineligible by automation tools" として**スクリーニングの手前**に置き、
**人手除外とは分けて報告する**ことを求めているが、補完後の再適用は
**検索が一度も見ていないテキストで自動除外を発動させる**ことになる。

さらに Phase 1.5 のフェイルセーフ（`hold` = 判定不能なので人手に委ねる）は
「メタデータが欠けているから除外」を避けるための設計であり、再適用は
「メタデータが後から手に入ったから除外」となって目的と逆行する。文献が残るかどうかが
Semantic Scholar のカバレッジ（実測48%）に左右されるのも受け入れがたい。

**採った立場: 補完は人手判定の材料としてのみ使う。パイプラインは一切変更しない。**
判定対象1,052件は不変。

> **前例の状況（正直な記録）**: メタデータ補完自体は標準（重複削除で「最も完全なメタデータを
> 持つ版を残す」のは通常の運用で、Rev.13 のマージも同じ）。自動ツールによる除外も
> PRISMA 2020 に専用の箱があり標準。しかし **その2つを連結した運用**
> （外部APIで補完したテキストに自動除外を掛け直す）の前例は見つけられなかった。

#### 途中で直した不具合: 「要旨が無い」と「取れなかった」の混同

初回実行で S2 の取得が74件で頭打ちになり、以降が全部「未取得」になった。原因は
**429（レート制限）** で、共有関数のバックオフ（0.5→1→2秒）が短すぎた。

より重大だったのは、**「HTTP 200 + `abstract: null`（本当に要旨が無い）」と
「429 で取れなかった」を区別せず両方 `notfound` に記録していた**こと。これでは
「この論文には要旨が存在しない」という誤った記録が残り、再試行の機会も失われる。
状態を4つ（`ok` / `notfound` / `ratelimited` / `error`）に分け、`ratelimited` は
次回実行で自動再試行されるようにした。

**ただしレート制限の影響は当初の見立てより小さかった。** 149件を再試行した結果、
**143件は本当に要旨が存在せず**、回収できたのは3件のみ。修正自体は必要（誤った記録を
残さないため）だが、取得件数への寄与は限定的だった。推測で「大量に取り逃がしている」と
判断せず実測したのは正しかった。

#### 成果物

- `scripts/enrich_screening_abstracts.py`（新規）— 補完を独立した工程にした。
  シートを直接書き換えると再生成で消えるため、DOI をキーにした再利用可能なキャッシュ
  （`outputs/enriched_abstracts.csv`）として外に置く
- 判定シートに **`abstract_source` 列**（`database` / `enriched` / `none`）。CSV・xlsx とも対応
- Excel 版では列ヘッダのコメントと「はじめに」シートに説明を追加

#### 残る191件について

タイトルのみでの判定になる。引用探索側に偏っている（128件）のは、引用メタデータが
DOI しか持たないことが多く S2 側にも要旨が無いため。**Threats to Validity に件数と
経路別内訳を記載すること。** シートでは `abstract_source=none` と淡い赤の行で識別でき、
「はじめに」シートに「無理なら Unsure にしてください」と明記してある。

#### 次回やること

1. **判定シートの配布 → Phase 3b 開始**（1,052件・約701件/人）。配布前の懸案は解消した
2. タイトル取得不能3件の手作業同定（`snowballing_protocol.md` §4.4）
3. Phase 3b 完了後に `score_screening.py` で κ 算出・協議リスト生成

#### ⚠️ 未処理の作業ツリー汚染

リポジトリ直下に **`PROGRESS_LOG.md`（未追跡）** が存在する。2026-07-21 のコミット `7a27187`
で `docs/` へ移動したはずのファイルで、**内容も同時期（7月中旬）の古いもの**。
誰がいつ復活させたか不明なため**削除せず残してある**。`docs/log/PROGRESS_LOG.md` が正であり、
ルート側は不要と判断できれば削除してよい。

### 2026-08-17 (2) — Rev.17: Phase 3b を liberal accelerated 方式へ変更

著者から「Abstract 判定を1人でやって全文を配布する案はどうか」という提起があり、
実証研究を確認したうえで**中間解（liberal accelerated）を採用**した。

#### 検討した選択肢と実測

| 案 | 著者 | 他2名(各) | 見落とし | κ |
|---|---|---|---|---|
| 現行（Rev.9 ペア分担） | 681 | 696/727 | 3% | ◎ |
| **著者単独 + 全文配布** | **1,052** | **0** | **13%** | **算出不能** |
| **liberal accelerated（採用）** | 1,052 | ~346/308 | 3%相当 | ○（校正セット） |
| 単独 + 一部二重チェック | 1,052 | ~52-105 | 13% | △ |
| Fleiss' κ | 1,052 | 1,052 | 3% | ◎（Rev.9 で却下済み） |

**単独スクリーニングは関連文献の13%を見落とす**（2名体制は3%）という RCT の実測があり、
「systematic review に期待される方法論的水準を満たさない。rapid review では有効な選択肢」と
評価されている。CSUR 投稿は rapid review の枠に入らないため採らなかった。

**気づいた点として、単独案は著者の負担がむしろ最大**（681→1,052）になり、
負担軽減の手段としても成立しない。負担の所在が「他2名」なのか「著者」なのかで
選ぶべき案が変わる、という整理を提示したうえで著者が liberal accelerated を選択した。

#### 採用した設計

> **1名が Include にすれば通す。Exclude するには2名必要。**

```
stage 1  著者が全1,052件を判定 + 校正セット164件(15%)は3名全員が判定
stage 2  著者が Exclude / Unsure にしたものだけ第2評価者が確認
```

**根拠は Phase 3b のエラーの非対称性。** 誤 Exclude は回復不能（全文を読む機会が永久に
失われる）だが、誤 Include は Phase 4 の手間が増えるだけ。**除外の方向にだけ2名を要求**
すれば、工数を抑えつつ感度を保てる。本プロトコルが既に採る「除外できると確信できないものは
残す」「解決しなければ Include に倒す」という再現率優先の思想とも一致する。

#### ★ 実装前に判明した制約と、当初説明の訂正

**選択肢を比較した際に「liberal accelerated なら κ を算出できる」と述べたが、これは誤りだった。**

除外プールだけで Cohen's κ を計算すると、著者側の判定が定義上すべて Exclude で分散が無いため
**Pe = Po となり、実際の一致率によらず κ が常に厳密に 0** になる。実装前に数値で確認した:

```
第2評価者が 100/200 件を Exclude → κ=0.000
第2評価者が 190/200 件を Exclude → κ=0.000   ← 95%一致でも 0
```

したがって **3名全員が全判定を行う校正セットが必須**。判定対象の15%（164件）を
決定論的に抽出して κ の算出基盤とした。副次的に、本作業前の判断基準のすり合わせ
（calibration exercise）にもなる。

#### 実装

- **`make_screening_stage2.py`（新規）** — 著者の記入完了後、Exclude/Unsure だけを
  第2評価者に配る。**著者の判定は見せない**（判定列を空にして独立性を担保）
- `make_screening_sheets.py` — 校正セットの決定論的抽出（`is_calibration`）と
  第2評価者の振り分け（`second_reviewer_of`）。`calibration` 列を追加
- `score_screening.py` — κ を**校正セットのみ**で算出。Include は
  「liberal accelerated で1名通過」として協議対象から外し、内訳を表示
- `make_screening_xlsx.py` — `--prefix stage2_` で stage 2 シートにも対応

模擬記入で全フロー（stage 1 → stage 2 生成 → κ 算出 → 協議リスト）を検証し、
κ が校正セットで正しく算出される（0 にならない）ことを確認した。

```
模擬実行: 著者の判定 Include 562 / Exclude 282 / Unsure 44 / 校正164
  → stage 2  Kataoka 182件 / WATANABE 144件
  → κ(校正164件)  著者×K 0.473 / 著者×W 0.418 / K×W 0.436  平均 0.443 moderate
```

#### 文書の見直し

- `rule.md` Phase 3b を全面改訂。**Phase 4 は通常の二重評価のまま**とし、
  その理由（非対称性は Title/Abstract 段に固有。全文評価は最終判断で双方に同等の慎重さが要る）を明記
- `screening_protocol.md` §0 を改訂、stage 2 の節を新設、節番号の重複を修正
- **README に §11「Phase 3b: 人手スクリーニングの実施」を新設**。
  実行手順・設計上の要点・報告に必要な数値。ファイル構成に `screening/` と
  スクリーニング系スクリプト4本を追加（監査で抜けが判明した）
- 常設セクションに残っていた旧体制の記述（「3名ペア分担で約701件/人」2箇所）を是正
- 原稿の Phase 3b を書き直し、根拠論文（Gartlehner et al. 2020）を引用に追加。
  κ が0になる制約を本文でも説明した（査読で必ず問われる点のため）

#### 次回やること

1. **判定シートの配布 → stage 1 開始**
2. 著者の stage 1 完了後に `make_screening_stage2.py` → 第2評価者へ配布
3. 全員完了後に `score_screening.py` で κ 算出・協議リスト生成

### 2026-08-17 (3) — 配布用の記入見本を作成

配布時に「どう記入すればよいか」を示す見本が必要になったため作成した。

#### 判定そのものは実行していない

著者から「私の分の判定を実行して見本として見せたい」という依頼があったが、
**`rule.md` Rev.2 が「包含/除外判定に LLM を一切使用しない」と定めており**、
原稿にも "no large language model was used at any eligibility decision point" と
記載しているため、判定対象1,052件には一切触れていない。査読で最も強く主張している
方法論的特徴が崩れるためである。

代わりに**記入見本**（5件）を作成した。「配布時に見せる」という目的にはこちらが直接的。

#### 汚染しない設計

見本の素材は**すべて判定対象1,052件の外**から採った。

- Phase 3a で機械的に除外済みの文献（除外理由が決定論的に記録済み）
- gold set のうち判定対象に含まれないもの（著者が既に分類済み）

つまり見本の判定は**新しい判断ではなく既存の記録の転記**である。
`record_id` を `EXAMPLE-n` とし、`assignment.csv` に載らないため集計からも構造的に除外される。
スクリプトに**汚染チェック**を組み込み、見本の DOI が判定対象に含まれていればエラーで停止する。
生成時に重複0件を確認済み。

#### 見本の内容

Include の典型例1件、Exclude 3件（P / I / S 基準それぞれ）、Unsure 1件。
各行の `note` 列に「なぜそう書いたか」の解説を入れ、「はじめに」シートに PICOS の要約と
**「除外できると確信できないものは残す」**という原則を書いた
（この段階の誤除外は回復不能であるため）。

#### 著者への申し送り

**配布前に見本の判定・理由を確認すること。** 形式を示すためのものだが、配布時には
「著者の判断」として提示される。書き換えるなら `scripts/make_screening_example.py` の
`EXAMPLES` を編集して再実行する。

### 2026-08-19 — Rev.18: 除外理由の統制語彙、screening/README、出典の集約、そして**シート配布と凍結**

配布直前の整備を行い、**判定シートを評価者へ配布した。Phase 3b の設計はここで凍結**。

#### 🛑 凍結（最重要）

**2026-08-19 に Phase 3b の判定シートを配布した。** 以降、判定基準・除外理由の語彙・
割当・シート構成は**一切変更しない**。

- `make_screening_xlsx.py --force` は評価者の記入済み判定を破棄する。**実行しない**
- `pipeline.py` の再実行も禁止（step ファイルが上書きされ、配布済みシートと対応が取れない）
- 配布後に基準を変えると評価者ごとに適用された基準が異なることになり、
  **κ も除外理由の集計も意味を失う**

変更が必要になった場合はシートを作り直さず、`protocol_changelog.md` に逸脱として記録し
Threats to Validity で報告する。凍結解除は著者の明示的な指示があるときだけ。
告知は `rule.md` §Phase 3b・`docs/protocol/screening_protocol.md`・`screening/README.md`・
`.claude/skills/survey-pipeline/SKILL.md` の4箇所に置いた。

読み取りは自由。`score_screening.py` による記入状況の確認と、
著者の stage 1 完了後の stage 2 生成は想定内の運用であり凍結の対象外。

#### Rev.18: 除外理由を統制語彙（ドロップダウン）に

判定シートの `reason` 列を自由記述から9択のドロップダウンへ変更した（PR #10、マージ済み）。

理由は、PRISMA 2020 が除外理由の記録を求める一方、**自由記述では事後に数えられない**こと。
統制語彙なら「理由別の除外件数」をそのまま本文の表に出せる。自由記述のままだと著者が
事後にコーディングすることになり、**その作業自体が判定への事後介入**になる。
加えて評価者3名で表記が割れると同じ理由が別物として集計される。

選択肢: `P: 対象者が不適合` / `I: HMD-VR でない` / `I: スケール操作/多感覚刺激が無い` /
`O: スケール知覚の測定が無い` / `S: ユーザー実験が無い` / `S: 原著論文でない` /
`スコープ外(主題が無関係)` / `重複(同一研究の別報告)` / `その他`

- **`C`（比較対象）は含めない。** 比較条件は要旨に記載されないことが多く、
  Title/Abstract 段で C を根拠に除外すると誤除外（回復不能）を招く。判断は Phase 4 へ送る。
- **`その他` は残した。** 閉じた語彙は当てはまらない事例を既存カテゴリへ押し込ませる。
  逃げ道を用意したうえで**メモへの記述を必須**にし、件数が増えたら語彙を見直せる状態を保つ。
  **「その他」の件数と内訳は Threats to Validity で報告する。**
- 複数該当時は最も明白なものを1つ選び、残りはメモへ（PRISMA の primary reason 慣行）。

実装: 選択肢は Excel の隠しシート `_選択肢` に置いて範囲参照した
（**インラインの選択肢リストは Excel 仕様で 255 文字上限**があり日本語では溢れるため）。
「はじめに」シートの語彙表と記入見本は `EXCLUDE_REASONS` から自動展開して二重管理を避けた。
`score_screening.py` に「語彙外の値」「その他なのにメモが空」の検査と、
**理由別の除外件数の出力**を追加した。合成データで3つの検査の発火を確認済み。

#### `screening/README.md` の新設

`screening/` 一式は supplementary material として公開する前提だが、フォルダ単体では
何のファイルなのか分からない状態だった。方式・各ファイルの役割・統制語彙・再現手順・
既知の制約・バージョン管理での扱いを収めた。
記載した数値はすべて `sheet_author.csv` と `assignment.csv` に突き合わせて検証した。

**stage 2 のシートを事前に配れない理由**も明記した。判定列を空にしてあっても、
そこに含まれること自体が「著者が Exclude / Unsure にした」という情報になるため。

#### 方法論の出典を `rule.md` §5 に集約

「単独スクリーニングは関連文献の 13% を見落とす（2名体制は 3%）」が**出典なしで4文書に
重複**していた。根拠を特定し、`rule.md` に §5 を新設して [R1] として収録した。

> Gartlehner G, Affengruber L, Titscher V, Noel-Storr A, Dooley G, Ballarini N, König F.
> Single-reviewer abstract screening missed 13 percent of relevant studies: a crowd-based,
> randomized controlled trial. *J Clin Epidemiol* 121:20-28 (2020).
> DOI: 10.1016/j.jclinepi.2020.01.005

数値（13% / 感度 86.6% / CI 80.6-91.2、3% / 97.5% / 95.1-98.8）の一致を確認済み。

**§5 には引用時の注意も併記した。** この論文が検証したのは1名 vs 2名であって
liberal accelerated ではなく、結論も「rapid review では有効な選択肢」という条件付きである。
本サーベイは rapid review ではないため、そのまま援用すると過剰主張になる。

**未確認:** `liberal accelerated` という手法名の一次出典。Nama et al. (2021, *Syst Rev*
10:98) が本用語を定義したうえで Khangura et al. (2012, *Syst Rev* 1:10) に帰属させているが、
Khangura 2012 本文が当該語を用いているかは未確認（ペイウォール）。§5 に注記として残し、
正式収載していない。**本文で用語を引く前に一次資料の確認が必要。**

#### `/survey-pr` スキルの新設（PR #11、マージ済み）

PR を「コードが動くか」ではなく**「文書がコードと現実に一致しているか」を担保する地点**
と位置づけ、検証手順を明文化した。判定シートの混入チェック、実データとの突き合わせ、
「正」が1箇所のものと写しのずれ、出典の集約、コメントと実装の乖離、など。

チェック項目は一般論ではなく、このリポジトリで**実際に起きた乖離**を根拠にしている。

#### 技術的な積み残しの処理

- `make_screening_stage2.py` の docstring が「著者が Exclude にしたレコードだけ」と
  書いていたが、実装（74-87行目）は **Unsure も第2評価者へ回す**。docstring のみ修正
  （動作は不変）。あわせて 13% の出典を §5 [R1] 参照にした
- `.claude/skills/survey-pipeline/SKILL.md` が `ResearchVR2.csv` / 14,385件 /
  最終候補1,784件のままだった。現行値（26,434 → 18,342 → 6,317 → 1,179 → 795、
  判定対象1,052件）へ更新。Phase 1.5 が抜けていたので追加し、
  「rule.md の Phase 3（LLM要旨判定）は未実装」という**Rev.2 と矛盾する記述を削除**した。
  数値は step ファイルの実行数を数えて README・PROGRESS_LOG と一致することを確認済み

#### 次回やること

1. **著者の stage 1 判定 1,052件**（最優先・クリティカルパス）。
   Kataoka / WATANABE の校正セット164件は並行して進む
2. stage 1 完了後: `make_screening_stage2.py` → `--prefix stage2_` で stage 2 を生成・配布
3. 全員完了後: `score_screening.py` で κ・理由別内訳を算出 → 協議 → `final_decisions.csv`
4. `liberal accelerated` の一次出典（Khangura 2012）の確認
5. `README.md` §7 の追加分析が旧データ（1,784件時点）のまま。更新するか判断する
   （本人が「未更新」と明記しているので、消さずに注記を残すこと）


### 2026-08-19 (2) — 評価者向け説明資料 / Known-Item の判定対象への残存を照合

#### 説明資料（`docs/reference/reviewer_briefing.md`）

評価者2名から「経緯を把握できていない、**特にどういった論文を対象にしているか理解したい**」
という依頼があり、8/20 に30分の説明会を設けることになった。前回説明が Rev.9 時点だったため
Rev.10〜19 を差分として扱い、Rev.15 / Rev.17 / Rev.18 に印を付けた。締切は **2026-08-26**。

対象論文の説明は**実例から入る**構成にした。抽象的な PICOS より gold set の適合論文17件を
実物で見せるほうが早い。読み取ってほしい3点を明示した:
心理・認知系の雑誌も対象であること、2ページのポスターも対象であること、そして
**視覚のみ14件 vs 多感覚3件という偏りこそが本研究の主張**であること。
3点目は「多感覚を扱っていないから物足りない=除外」と誤解されると RQ1・RQ3 の分母が
失われるため特に強調した。

**凍結との整合を冒頭と想定Q&Aに明記した。** 配布後に説明会で基準を口頭で変えると、
説明の前後で適用基準が変わり κ が壊れる。基準の解釈に関わる質問はその場で回答せず
持ち帰る運用とし、迷った個別文献は `Unsure` に倒してもらう。

#### ★ Known-Item が判定対象に残っているかの照合（新規計測）

資料に gold set 17件のタイトルを載せることの是非を確認するため照合した。
新規スクリプト `scripts/known_item_screening_audit.py`（読み取り専用、
出力 `outputs/known_item_in_screening.csv`）。

**当初の懸念は解消。** 判定対象1,052件に含まれるのは8件だが、
**校正セット164件に含まれるのは0件**。κ は校正セットでのみ算出するので影響は無い。
含まれる8件を判定するのは著者（stage 1）のみで、著者は gold set の作成者であり
新たな汚染は生じない。さらに著者が Include にすれば stage 2 にも回らない。

**副産物として、スノーボーリングの寄与が定量化できた。**

| 対象 | 残存 | recall |
|---|---|---|
| DB検索のみ（`known_item_test.py` の step3 = 795件） | 5/17 | 29.4% |
| 判定対象 1,052件（引用探索 257件を加算） | **8/17** | **47.1%** |

引用探索が3件（Being Barbie 2011 / plausibility paradox 2020・2021）を回収していた。
**Being Barbie は `known_item_analysis.md` が「G1に命中せず検索式が構造的に取りこぼす」
と特定していた文献**であり、ライブラリ追加では直らないと分析されていた。
**クエリのギャップを引用探索が実際に埋めた**直接的な証拠になる。

`known_item_test.py` は step ファイル（DB検索側）だけを対象にしており、
引用探索分を勘定に入れていないため、この数値はこれまで未計測だった。
Threats to Validity 転用可の形で `docs/protocol/snowballing_protocol.md` §4.7 に記録した。

> **報告時の注意:** 47.1% は依然として低い。「引用探索で解決した」ではなく
> **「29.4% → 47.1% に改善したが限界が残る」**が正確な記述。残る9件の脱落理由
> （Venue ホワイトリスト・クエリのG1ギャップ）とあわせて報告すること。

#### 次回やること

前回（2026-08-19）の一覧から変更なし。最優先は**著者の stage 1 判定 1,052件**。
評価者2名の校正セット164件は締切 2026-08-26 で並行して進む。

### 2026-08-20 — Rev.20: S基準の語彙矛盾を発見・解消 / 事前配布資料の作成とPDF組版

説明会（本日）に向けて、評価者から事前に届いた3つの質問（①研究分野と対象論文、
②プロセスが必要な背景、③打ち合わせで説明してほしいこと=ファイル・記入粒度・例題）
に答える資料を作成した。その過程で**配布済み文書どうしの矛盾を1件発見し、Rev.20 として処理した。**

#### ★ Rev.20: 除外理由語彙と Rev.14 の S 基準運用が矛盾していた

**発見。** Rev.18 の統制語彙 `S: 原著論文でない` の定義に**「ポスター」**が含まれていた。
これは Rev.14（2026-08-15）で確定した著者判断——「2ページのポスター/ショートペーパーも、
実験を報告していれば実証研究として含める。ページ数ではなく内容で判断する」——と正面から矛盾する。
Rev.18 で自由記述を統制語彙に置き換えた際、Rev.14 の運用判断が語彙定義に反映されず脱落していた。

**配布物どうしが食い違っていた。** `sheet_*.xlsx` の `_選択肢`／「はじめに」シート、
`screening_protocol.md` §139、`screening/README.md` には「ポスター」が入っている一方、
`reviewer_briefing.md` §2.4 の表には無く、同 §2.1(2)・§2.5 は「2ページのポスター・
アブストラクトも実験があれば Include」と明記していた。

**実害を確認した。gold set の in-scope 17件のうち4件が2ページの会議論文**で、
語彙どおりに機械適用すると全て脱落する。

| 文献 | 掲載先 | 位置づけ |
|---|---|---|
| Sikström et al. 2015 | IEEE VR 283-284 | **最重要。in-scope で唯一の聴覚の例**（Rev.14 で「聴覚の穴を埋める」目的で追加したもの） |
| Okada et al. 2025 | IEEE VRW 1232-1233 | 必須。触覚 × 体サイズ |
| Ogawa et al. 2018 | IEEE VR 647-648 | 推奨 |
| Zhao & Madhavan 2013 | IEEE VR 149-150 | 推奨 |

**著者判断 = 方針(b): 語彙は変更せず、解釈の明示で解消する。**
配布済みシートの `_選択肢`／「はじめに」シートの文言は**そのまま残す**。
明示する解釈は「`S: 原著論文でない` は**実験を報告していない文献種別**を指す。
実験を報告しているポスター/ショートペーパーは Include。ページ数は除外理由にならない」。

理由は3点。(1) 語彙を変えるには xlsx 再生成が必要で、`--force` は記入済み判定を破棄する
（Rev.19 で禁止）。今回は記入0件なので実害は無いが、一度許すと前例になる。
(2) 配布した語彙と後日公開する語彙が食い違うと、除外理由の集計表がどの定義に基づくのか
第三者が追えない。**語彙は監査証跡として固定し、解釈は別レイヤで明示する**ほうが再現性が高い。
(3) **本日時点で3名とも記入0件**（author 0/1,052・kataoka 0/164・watanabe 0/164、
`openpyxl` で実測）。補足は説明会で3名同時に到達するため、
「記入の前後で適用基準が変わる」問題は生じない。Rev.19 の凍結が守る前提は保たれる。

反映先: `protocol_changelog.md` Rev.20（Threats に載せる4項目を明記）/
`reviewer_briefing_preread.{md,tex,pdf}` §4.3 /
`reviewer_briefing.md` §2.4 / `screening_protocol.md` / `screening/README.md`。
**`screening/README.md` には「stage 2 のシート生成時も語彙は変えず同じ補足を書面で添える」
と明記した。** stage2 シートの「はじめに」にも同じ語彙が再掲されるため、忘れると再発する。

#### 事前配布資料の作成（`reviewer_briefing_preread`）

既存の `reviewer_briefing.md` は内容は足りていたが長く、要点が届いていなかった。
**短い事前配布版を分離**し、Markdown（内容の正）+ LaTeX（配布用組版）+ PDF の3点構成にした。

- 組版は MiKTeX の **lualatex + ltjsarticle**。A4・5ページ、日本語フォント（原ノ味）埋め込み、
  Overfull 0・警告なし。中間ファイルは削除し `.gitignore` に追加した
- ビルド: `lualatex --interaction=nonstopmode docs/reference/reviewer_briefing_preread.tex`

**最大の内容上の修正は「164件と1,052件の関係」。** 評価者は
「164件の後に著者が1,052件を判定する」と理解していたが、**これは前後関係ではなく包含関係**。
164件は1,052件の部分集合で、stage 1 は3者並行。この訂正を図と時系列表で明示した。

#### ★ 例題に使える文献の安全性を照合（新規計測）

「1〜2件の論文を例に、該当するかどうかをすり合わせたい」という依頼に対し、
**どの文献なら例に使ってよいか**を `outputs/known_item_in_screening.csv` と
`assignment.csv` の突合で確定した。

| 区分 | 件数 | 例題への可否 |
|---|---|---|
| 判定対象1,052件に**含まれない** | **9件** | **安全。例題に使える** |
| 1,052件に含まれる（全て `calibration=N`） | 8件 | **使えない。stage 2 で kataoka 4件 / watanabe 4件 に配られる** |

前回（2026-08-19）の照合は「校正セット164件に0件」までで、**stage 2 での再出現を見ていなかった。**
κ は校正セットでのみ算出するので κ への影響は無いが、
「確実に対象」と見せた文献が後日その人の stage-2 シートに出ると独立性の前提が緩む。
資料の例題は**9件側だけ**を使う構成に差し替えた（Leyrer 2011 / Serino 2020 / Okada 2025）。
当初案の Being Barbie 2011 と Sikström 2015 はどちらも watanabe の stage-2 対象だったため除外。

> **`reviewer_briefing.md` §2.1 の gold set 17件の表は、8件を露出したまま。**
> 今回は変更していない。表を9件に絞るか、露出を Threats に記録するかは**著者の判断待ち**。

#### 要旨の中央値を訂正

資料に書いていた「中央値1,278字」は、**要旨が無い35件を0字として含めた中央値**だった。
要旨がある129件（校正セット）では **1,466字**、コーパス全体861件では 1,413字。
作業量の見積もりに直結するので事前配布版は 1,466字 に直した。
`screening_protocol.md` §99 と `reviewer_briefing.md` にはまだ 1,278 が残っている（軽微・未修正）。

#### 論文執筆側の skills を作成（`SelfScaleSurvey/`）

原稿リポジトリに `.claude/skills/` を新設し2本追加（コミット `13ee1ec`）。

- **`survey-paper`** — 章構成・taxonomy の作り方と提示・既存サーベイに対する positioning・
  Methodology の報告項目・`\prov{}`/`\pending{}` 運用。典拠は Mori らのサーベイ3本
  （DR survey 2017 / Radiance Fields in XR 2025 / AR Visualization Taxonomy 2021）と
  Stefanidi et al. "Literature Reviews in HCI: A Review of Reviews" (CHI 2023)、CSUR 編集方針。
  CHI 2023 の実測値（HCIレビュー189本中 IRR算出13% / PRISMAフロー23% / DB明記69%）は
  **本サーベイの厳密さを Methodology で主張する根拠**として使える
- **`paper-figures`** — `SelfScaleSurvey/docs/38_659.pdf`（人間ドック 2024 総説
  『論文における図表の作成』）の全77条を `rules.md` に逐条化 + acmart への落とし込み
- 副産物: **`main.tex` は表5・図0**。系統的レビューとして PRISMA フロー図が無いのは通らない。
  必要な図4点（PRISMAフロー / taxonomy全体図 / 年次分布 / modality×referent クロス集計）を列挙した

#### 次回やること

1. **著者の stage 1 判定 1,052件**（最優先・変更なし）。評価者2名の164件は締切 2026-08-26 で並行
2. `reviewer_briefing.md` §2.1 の gold set 表をどうするか判断（9件に絞る / Threats に記録）
3. `screening_protocol.md` §99・`reviewer_briefing.md` の「1,278字」を 1,466字 に訂正
4. リポジトリ直下の `PROGRESS_LOG.md`（2026-08-16 時点・15KB・未追跡）は
   `docs/` 集約前の残骸。**削除の可否は著者判断待ち**


### 2026-08-20 (2) — 説明会の質疑対応 / 手法の比較検討 / Rev.21: κ 閾値方針

#### 説明会で答えられなかった3問への回答（`methodology_rationale.md` §8-C）

1. **κ とは** — 偶然の一致を差し引いた一致度。実計算の対比例を載せた。
   どちらも90件を Include にしたケースで、**82%一致でも κ=0.000**（Pe=Po のため）。
2. **164件の出どころ** — `CALIBRATION_PCT = 15` で `md5("cal:"+key) % 100 < 15` により
   決定論的に抽出した結果が164件（15.59%）。164 を先に決めたのではない。
   **★ ただし「15%」という比率の根拠はどこにも記録されていないことが判明。**
3. **手法は正しいのか** — 標準の部分と非標準の部分を分けて答える構成にした。

#### ★ 手法の比較検討（`screening_method_alternatives.md` を新設）

文献調査で候補10件を比較。**最大の成果は、liberal accelerated が
Cochrane Rapid Reviews Methods Group の公式ガイダンスが推奨する手続きだったこと**
（[R3] Garritty et al. 2021）。一次出典も [R2] Khangura et al. 2012 で確定し、
Rev.18 以来「未確認」としていた穴が塞がった。

**同時に、本設計への具体的な指摘材料も出た**（[R4] Nussbaumer-Streit et al. 2023）:

| 指摘 | 対応 |
|---|---|
| 二重判定の割合として**20%**を例示（本研究は15%） | Threats に明記。反論の骨子は §2-D |
| 単独移行の**80%一致ゲート**（本設計に規定なし） | **Rev.21 の閾値方針で対応** |
| 除外確認方式は「時間の節約にならない」 | **正当化を工数から誤除外の回復不能性へ寄せる** |

出典 [R2]–[R8] を `rule.md` §5 に収録した（[R7][R8] は書誌未確定と明記）。

#### ★ Rev.21: κ が基準を下回った場合の対応（**結果を見る前に確定**）

これまで**未定義**だった。締切（8/26）より前に定めることで、後付けの疑いを排除する。

| κ（3カテゴリ版ペア平均） | 対応 |
|---|---|
| ≥ 0.61 | 予定どおり続行 |
| 0.41–0.60 | 全件協議 → **除外理由の分布を検査** → 特定基準に集中していれば全件再判定 |
| < 0.41 | stage 2 を拡大し**著者の Include も第2評価者が確認**（実質的な全件二重化） |

いずれかのペアが単独で 0.41 未満なら、そのペアに下位段を適用。
**校正セットの一部を除いた再計算 / 2カテゴリ版への切り替え / κ の不報告は明示的に禁止。**

**`score_screening.py` に `kappa_action()` として実装した。** 文書に書くだけでは
忘れられる（Rev.14 の判断が2度失われた）ため、集計時に自動表示される形にした。
4段階すべての発火を合成値で検証済み。

#### Phase 4 について

現行案（完全二重独立）の維持を推奨。[R6] の基準限定単独除外は魅力的だが、
検証領域が小児医療で、**「conference abstract は単独除外可」が本サーベイの
「実験を報告するポスターは Include」（Rev.14/Rev.20）と正面から衝突する**。
流用するなら P基準に限定すべき。

#### 次回やること

1. **著者の stage 1 判定 1,052件**（最優先・クリティカルパス）
2. 評価者2名の校正セット164件（締切 2026-08-26）
3. 締切後: `score_screening.py` → κ 算出 → **Rev.21 の閾値方針に従って対応**
4. 未決: `rule.md` Rev.2 の「AI/LLM」が古典的機械学習を含むか（候補F の可否）
5. 未決: [R7][R8] の書誌情報の特定
