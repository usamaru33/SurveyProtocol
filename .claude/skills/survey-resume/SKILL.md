---
name: survey-resume
description: VR自己スケール知覚サーベイの現状を思い出す。セッション開始時、「続きから」「今どこまで進んでた？」と言われたとき、久しぶりの再開時に使う。
---

# サーベイ再開（コンテキスト復元）

VR空間における自己スケール感覚のシステマティック・レビュー（PRISMA 2020準拠）プロジェクトの状況を復元する手順。

## 手順

1. 以下を読む（すべて `SurveyProtocol/` 内）:
   - `PROGRESS_LOG.md` — 進捗ログ。**最優先。**「完了していること」「まだやっていないこと」「セッションログ」を確認
   - `rule.md` — 研究プロトコル（目的・RQ・スクリーニング基準・Taxonomy）
   - `README.md` — パイプライン実装の詳細と PRISMA 数値
2. `git -C SurveyProtocol log --oneline -5` と `git status -s` で最後のコミット以降の差分を確認する。
3. ユーザーに「現在の到達点」と「次のアクション候補」を要約して提示してから作業に入る。

## 前提知識（要点）

- 最終候補は `step3_kw_included.csv`（1,784件）。パイプラインは Phase 1(重複削除)→2(Venueランク)→3(キーワード除外) まで実行済み。
- rule.md 本来の Phase 3（LLM要旨判定）と Phase 4（全文PICOS評価）は**未着手**。
- 兄弟フォルダ `docs-system/` は Semantic Scholar ベースの文献ブラウザ（Next.js）。サーベイ本体とは未接続。`DocsSystem/` は空（廃棄跡）。
- 作業終了時は必ず `/survey-log` で PROGRESS_LOG.md に追記する。
