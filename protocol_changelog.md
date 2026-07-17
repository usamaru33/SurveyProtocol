# Protocol Changelog — プロトコル変更履歴

> システマティック・レビューのプロトコル(`rule.md`)に対する全変更を日付つきで記録する。
> ACM Computing Surveys の方法論セクション(protocol deviations の報告)に転用するため、
> 各項目は「変更内容 / 変更理由 / 影響範囲」を明記する。

---

## 2026-07-16 — Rev.2: AI判定の全面廃止と人手ダブルスクリーニングへの置換

### 変更 1: 「Phase 3: AI支援による要旨判定」を削除し、Phase 3a / 3b に置換

- **旧:** LLM(Google Gemini)による要旨判定。HCI分野は保守的戦略(再現率優先)、
  心理分野はPICOS厳格照合(適合率優先)として分野別に分岐。判定後に無作為抽出の目視確認。
- **新:**
  - **Phase 3a:** 決定論的キーワード除外(正規表現、実装済み `pipeline.py`)。
    全除外パターンの追加理由をPICOS基準と対応づけて rule.md に明記。
  - **Phase 3b:** Title/Abstract の人手二重スクリーニング
    (評価者2名・独立判定・Cohen's κ 報告・不一致は協議、未解決は Include 側へ)。
- **理由:** ACM CSUR の再現性要件。LLM判定は
  (a) モデルバージョン依存で第三者再現が不可能、
  (b) プロンプト感度の報告方法が確立していない、
  (c) PRISMA / Kitchenham 系ガイドラインに標準手続きが存在しない。
- **影響範囲:** step3_kw_included.csv(1,784件)までの既存出力は Phase 3a に相当し**変更なし**。
  Phase 3b は未実施であり、以降の件数はこの変更の影響を受ける。
  rule.md の分野別分岐(HCI/心理)は AI 戦略の差に由来していたため、廃止に伴い単一フローに統合。

### 変更 2: Phase 1 として「重複削除」を明文化

- **旧:** rule.md に重複削除の記載なし(実装 `pipeline.py` には存在)。
- **新:** DOI → Zotero Key → 正規化タイトルの優先順位による決定論的重複削除を Phase 1 として明記。
- **理由:** 実装とプロトコル文書の整合。PRISMAフロー図の "Duplicates removed" に対応する手続きの明文化。
- **影響範囲:** 手続き自体は実行済み(14,385 → 12,442件)。数値の変更なし。

### 変更 3: CORE ランク基準の表記修正

- **旧:** 「学会ランク(CORE Ranking等)A以上を採用」
- **新:** 「CORE Ranking **A\* または A** のみ採用」
- **理由:** 実装(`HIGH_RANKS = {"A*", "A"}`)との厳密な整合。「A以上」という表現の曖昧性排除。
- **影響範囲:** 実装は当初からこの基準。数値の変更なし。

### 保留(未確定): SJR「Q1原則・不足時のみQ2」と実装(Q1のみ)の乖離

- **状況:** rule.md は「Q1原則・不足時のみQ2まで採用」だが、実装は Q1 のみ採用。
- **証拠:** Q2により脱落したのは **823件/332誌**(`outputs/sjr_q2_excluded_venues.csv`)。
  上位は臨床系(Journal of Clinical Medicine 34件、Frontiers in Neurology 23件等、
  Phase 3a Cat3 でどのみち除外される層)と LNCS(131件)だが、
  **IEEE Transactions on Haptics(13件)、Computer Animation and Virtual Worlds(15件)、
  Multisensory Research(3件)、Quarterly Journal of Experimental Psychology(6件)、
  Neuropsychologia(5件)** など主題関連誌を含む。
- **決定事項(著者判断待ち):** 本文を「Q1のみ」に合わせるか、実装を「Q2まで」に広げるか。
  rule.md 該当箇所に TODO コメントを埋め込み済み。決定後、本ファイルに Rev.3 として記録すること。

---

## 2026-05-25 以前 — Rev.1: 初版プロトコル

- rule.md 初版(検索戦略、AI支援スクリーニング、PICOS、Taxonomy 3軸)。
- `pipeline.py` による Phase 1〜3(現行番号で Phase 1 / 2 / 3a)を実装・実行
  (14,385 → 12,442 → 2,858 → 1,784件)。
