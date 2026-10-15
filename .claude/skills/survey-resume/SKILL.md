---
name: survey-resume
description: VR自己スケール知覚サーベイの現状を思い出す。セッション開始時、「続きから」「今どこまで進んでた？」と言われたとき、久しぶりの再開時に使う。
---

# サーベイ再開（コンテキスト復元）

VR空間における自己スケール感覚のシステマティック・レビュー（PRISMA 2020準拠）プロジェクトの状況を復元する手順。

## 手順

1. 以下を読む（プロトコル文書は 2026-07-21 に `SurveyProtocol/docs/` へ集約済み。README はルート据え置き）:
   - `docs/log/PROGRESS_LOG.md` — 進捗ログ。**最優先。**「完了していること」「まだやっていないこと」「セッションログ」を確認
   - `docs/protocol/rule.md` — 研究プロトコル（目的・RQ・スクリーニング基準・Taxonomy）
   - `README.md` — パイプライン実装の詳細と PRISMA 数値（§4 ファイル構成に docs/ の一覧あり）
   - `FILE_MAP.md` — どこに何があるかの索引（2026-10-15 追加） <!-- [2026-10-15 12:13 追加] 旧: (記載なし)。直前の README.md の行は変更していない -->
2. `git -C SurveyProtocol log --oneline -5` と `git status -s` で最後のコミット以降の差分を確認する。
3. ユーザーに「現在の到達点」と「次のアクション候補」を要約して提示してから作業に入る。

## 前提知識（要点）

- 最終候補は `data/pipeline/step3_kw_included.csv`（795件。Phase 3b の判定対象は引用探索257件を加えた1,052件）。パイプラインは Phase 1〜3a まで実行済みで凍結中。 <!-- [2026-10-15 12:13 更新] 旧: - 最終候補は `data/pipeline/step3_kw_included.csv`（1,784件）。パイプラインは Phase 1(重複削除)→2(Venueランク)→3(キーワード除外) まで実行済み。 -->
- Phase 3b（人手の二重スクリーニング。LLM は使わない、Rev.2）は stage 1・stage 2 を回収済みで、協議による最終判定を確定する段階（`screening/final/`）。Phase 4（全文PICOS評価）は全文 PDF の取得に着手した段階で、評価は未着手（`fulltext/`）。最新のプロトコルは Rev.27。 <!-- [2026-10-15 12:13 更新] 旧: - rule.md 本来の Phase 3（LLM要旨判定）と Phase 4（全文PICOS評価）は**未着手**。 -->
- 兄弟フォルダ `docs-system/` は Semantic Scholar ベースの文献ブラウザ（Next.js）。サーベイ本体とは未接続。`DocsSystem/` は空（廃棄跡）。
- 作業終了時は必ず `/survey-log` で PROGRESS_LOG.md に追記する。
- PR を作るときは必ず `/survey-pr` を通す（全文書への反映漏れを検証する手順）。
