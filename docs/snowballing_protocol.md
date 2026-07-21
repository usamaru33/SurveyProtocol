# Snowballing Protocol — 引用探索による補完手続き

> PRISMA 2020「Identification of studies via **other methods**」(フロー図右カラム、
> "Citation searching" の行)に計上する補完検索の手順。
> **なぜ必要か:** `methodology_decision_Rev7.md` の最重要発見 — Known-Item 13件中 **6件が
> Venue ホワイトリスト(CORE A\*/A + SJR Q1)で step2 脱落**(`outputs/venue_dropped_known_items.csv`)。
> これは検索式や DB 構成の問題ではなく、厳格な venue 品質フィルタによる学際/ワークショップ会場の
> 取りこぼしである。この構造的な漏れをスノーボーリングで回収し、透明に報告する。
>
> 決定論的・手作業ベースで、LLM は使わない。既存 step ファイルは変更しない。

---

## 1. 対象(シード)の選び方

スノーボーリングの起点(seed set)は**恣意的に広げない**。以下に限定する:

1. **step2 で脱落した Known-Item 6件**(`outputs/venue_dropped_known_items.csv`)。
   これらは著者が「必ず含まれるべき」と事前判断した文献であり、回収の第一優先。
2. **最終候補(step3_kw_included.csv)に生存した高中心性の文献**のうち、著者が
   レビューの柱(Intro/RW/Taxonomy の引用予定)に据えるもの。数を絞る(例: 10〜20件)。
3. Known-Item のうち **background(#19 Botvinick&Cohen 1998, #20 Lenggenhager 2007 等)**は、
   心理接合点の境界を示す文献として**後方探索の到達目標**に使う(これらに辿り着けるかで
   接合点カバレッジを点検)。ただし非VRのため本レビューへの採否は PICOS で個別判断。

> **区別の明記:** シード自体(step3 生存分)は既にDB検索で捕捉済みなので二重計上しない。
> スノーボーリングで**新たに**発見され、かつDB検索の統合データに不在の文献のみを
> "other methods" に計上する。

## 2. 手続き

### 2.1 後方探索(backward / 引用文献をたどる)

- 各シードの**参考文献リスト**を精査し、主題(VR × 自己スケール/身体化)に適合する
  候補を抽出する。
- 出典は原著PDFの References。補助的に Crossref / Semantic Scholar の
  "references" を用いてよい(件数確認のみ。採否は本文で判断)。

### 2.2 前方探索(forward / 被引用をたどる)

- 各シードを**引用している**新しい文献を Google Scholar / Semantic Scholar の
  "Cited by" で辿り、主題適合の候補を抽出する。
- step2 脱落の below_rank 会場(Presence, ICAT-EGVE 等)の重要論文は、
  後続の A\*/A・Q1 会場論文から前方探索で回収できることが多い。

### 2.3 反復と停止

- 新たに採用した文献をシードに加えて 1 回だけ反復する(2 ホップまで)。
- 新規採用が実務的にゼロに収束したら停止する。**反復回数と各回の新規件数を記録**する。

## 3. 採否判定(既存基準と同一)

- スノーボーリングで得た候補も、**本編と同じ PICOS / Phase 3b の人手基準**で採否を判定する。
  検索経路が違うだけで、包含基準は緩めない。
- **Venue ランク(CORE/SJR)基準の適用について**は、脱落カテゴリ別に扱う
  (`outputs/venue_dropped_known_items.csv` の `drop_category`):
  - `criterion`(例 #14 Gulliver, SJR Q2): 品質基準どおりの除外。**原則として本編には復帰させず**、
    Threats to Validity で「Q1限定により失われた主題関連文献」として報告する。
  - `unmatched`(例 #7/#8/#13, リスト未照合): まず `venue_aliases.csv`・正規化での救済を試す
    (`normalization_design.md`)。救済で A\*/A・Q1 に照合されれば step2 に復帰。
    真にランキング未収載(ワークショップ等)なら、スノーボーリングでの回収+個別判断。
  - `below_rank`(例 #3 Presence=CORE C, #10 ICAT-EGVE=CORE C): 会場はリストにあるがランク不足。
    品質基準を貫くなら除外維持。ただし当該文献が seminal(#3 Kilteni 2012 は用語定義の典拠)な場合は、
    **「Known-Item として著者が必須と判断した文献の限定的復帰」**を Threats に明記のうえ許容してよい。
    判断と理由を PROGRESS_LOG.md に必ず記録する。

## 4. 記録と PRISMA 報告

- 発見・採否を `outputs/snowballing_log.csv` に記録する(列の推奨):
  `seed_# , direction(backward/forward), found_title, found_doi, in_db_already(Y/N),
   picos_decision(include/exclude), venue_rank_note, reason`。
- **PRISMA 2020 フロー図**:
  - DB検索の統合(14,682 → …)とは**別カラム**("Identification of studies via other methods")。
  - "Records identified via citation searching (n = X)" にスノーボーリング新規発見数、
    "Studies included via other methods (n = Y)" に最終採用数を記す。
  - Frontiers in VR の journal hand-search(`search_replication.md`)も同じ右カラム側だが、
    "Websites/Organisations" 行として **citation searching とは別行**に分けて計上する。
- 本文の検索戦略節に1段落: 「厳格な venue 品質フィルタ(CORE A\*/A + SJR Q1)により
  学際/ワークショップ会場の主題関連文献が脱落しうるため、Known-Item Test で同定した脱落
  (`outputs/venue_dropped_known_items.csv`)を起点にスノーボーリングを実施した」旨を明記する。

## 5. 完了チェックリスト

- [ ] step2 脱落 Known-Item 6件すべてについて回収可否と最終判断を記録した
- [ ] `outputs/snowballing_log.csv` に全候補の採否・理由・DB既出フラグがある
- [ ] `in_db_already = Y` の文献を "other methods" に二重計上していない
- [ ] PRISMA 右カラム(citation searching / hand-search)の n を確定した
- [ ] below_rank/criterion の限定復帰があれば Threats to Validity と PROGRESS_LOG.md に記録した
