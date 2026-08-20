#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRISMA 3-Phase Screening Pipeline
==================================
Phase 1: 重複削除
Phase 2: 学会ランク A/A* 絞り込み (CORE.csv 参照)
Phase 3: キーワードマッチングによる除外

各フェーズで詳細ログと結果CSVを個別出力。
"""

from __future__ import annotations
import argparse, csv, re, sys
from collections import defaultdict
from pathlib import Path
import difflib

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
DEFAULT_INPUT   = _HERE / "ResearchVR2.csv"
DEFAULT_CORE    = _HERE / "CORE.csv"
DEFAULT_SJR     = _HERE / "scimagojr 2025.csv"
DEFAULT_ALIASES = _HERE / "venue_aliases.csv"
DEFAULT_OUTDIR  = _HERE

# ---------------------------------------------------------------------------
# Column aliases
# ---------------------------------------------------------------------------
TITLE_ALIASES    = ["Title", "title", "TITLE"]
ABSTRACT_ALIASES = ["Abstract Note", "Abstract", "abstract", "ABSTRACT",
                     "abstract_note", "AbstractNote"]
VENUE_ALIASES    = ["Publication Title", "publication_title", "Venue",
                    "journal", "booktitle", "Conference Name", "Meeting Name"]
DOI_ALIASES      = ["DOI", "doi"]
KEY_ALIASES      = ["Key", "key"]
ISSN_ALIASES     = ["ISSN", "issn", "ISBN"]

# ---------------------------------------------------------------------------
# CORE rank priority  (高いほど上位)
# ---------------------------------------------------------------------------
RANK_ORDER = {"A*": 4, "A": 3, "B": 2, "C": 1}
HIGH_RANKS = {"A*", "A"}   # Phase 2 で採用するランク

# ---------------------------------------------------------------------------
# Keyword Exclusion Categories  (Phase 3)
# ---------------------------------------------------------------------------
EXCLUSION_CATEGORIES: list[tuple[str, list[str]]] = [
    (
        "Cat1 [Not VR / Out of Scope]",
        [
            r"\bdesktop display\b", r"\bdesktop monitor\b", r"\bcomputer monitor\b",
            r"\bflat[- ]screen\b", r"\bflat panel\b", r"\b2d display\b",
            r"\baugmented reality\b", r"\bmixed reality\b",
            r"\bar\b", r"\bmr\b",
            r"\b360[- ]?(?:degree[s]?\s+)?video\b", r"\bspherical video\b",
            r"\bpanoramic video\b", r"\bomnidirectional video\b",
            r"\bsmartphone\b", r"\bmobile phone\b", r"\btablet(?:\s+computer)?\b",
            r"\bprojection mapping\b", r"\bprojected display\b",
            r"\bcave automatic virtual\b", r"\bcave system\b", r"\bcave display\b",
        ],
    ),
    (
        "Cat2 [Tech / Non-Empirical]",
        [
            r"\brendering\s+(?:algorithm|engine|pipeline|technique|performance)\b",
            r"\breal[- ]?time\s+rendering\b", r"\bshader\b", r"\bgpu\b",
            r"\bpoint\s+cloud\b", r"\bdepth\s+camera\b", r"\bstereo\s+reconstruction\b",
            r"\bmotion[- ]to[- ]photon\b", r"\bframe\s+rate\b", r"\brefresh\s+rate\b",
            r"\btracking\s+algorithm\b", r"\bsegmentation\s+algorithm\b",
            r"\boptimiz(?:ation|ing)\s+algorithm\b",
            r"\btechnical\s+report\b", r"\bsystem\s+architecture\b",
            r"\bsoftware\s+(?:framework|architecture|library)\b",
        ],
    ),
    (
        "Cat3 [Clinical / Medical]",
        [
            r"\brehabilitation\b", r"\bphysical\s+therapy\b",
            r"\boccupational\s+therapy\b",
            r"\bcognitive\s+(?:behavioural|behavioral)\s+therapy\b",
            r"\bexposure\s+therapy\b", r"\btherapeutic\s+intervention\b",
            r"\bsurgical\s+(?:training|simulation|procedure|planning)\b",
            r"\bsurgery\b", r"\blaparoscop\w+\b", r"\bminimally\s+invasive\b",
            r"\bstroke\s+(?:patient|rehabilitation|survivor|recovery)\b",
            r"\bpatient[s]?\b",
            r"\bclinical\s+(?:trial|study|outcome|setting|population)\b",
            r"\bphobia\b", r"\bptsd\b", r"\bpost[- ]traumatic\s+stress\b",
            r"\bautism\s+spectrum\b", r"\bdementia\b", r"\balzheimer\b",
            r"\bchronic\s+pain\b", r"\bpain\s+management\b", r"\bpain\s+relief\b",
            r"\bneurological\s+(?:disorder|condition|rehabilitation|disease)\b",
            r"\bpsychiatric\s+(?:disorder|treatment|patient)\b",
            r"\bpsychosis\b", r"\bschizophrenia\b",
        ],
    ),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_col(fieldnames: list[str], aliases: list[str]) -> str | None:
    for a in aliases:
        if a in fieldnames:
            return a
    return None


def normalize_venue(name: str) -> str:
    if not name:
        return ""
    n = name.lower()
    # Remove 4-digit years (e.g. 2010, 2024)
    n = re.sub(r"\b\d{4}\b", " ", n)
    # Remove ordinals (e.g. 1st, 2nd, 3rd, 10th)
    n = re.sub(r"\b\d+(?:st|nd|rd|th)\b", " ", n)
    # Remove parenthesised content entirely (e.g. "(VR)", "(ISMAR)", "(CW)")
    n = re.sub(r"\([^)]*\)", " ", n)
    # Remove non-word characters
    n = re.sub(r"[^\w\s]", " ", n)
    stop = [
        r"proceedings\s+of", r"proc\s+of", r"proc",
        r"conference\s+on", r"journal\s+of", r"transactions\s+on",
        r"symposium\s+on", r"international", r"the", r"of", r"on",
        r"in", r"and",
        r"annual", r"workshop", r"adjunct", r"abstracts",
        r"workshops", r"poster", r"posters",
    ]
    for sw in stop:
        n = re.sub(r"\b" + sw + r"\b", " ", n)
    return re.sub(r"\s+", " ", n).strip()


# ---------------------------------------------------------------------------
# Venue 正規化の構造ガード(Rev.12、docs/reference/normalization_design.md の案1/3/4/6)
#
# 現行の積極的な正規化はストップワードで種別語(journal of / transactions on /
# conference on / symposium on / workshop)まで落とすため、**ジャーナルと会議が
# 同一キーに融合する**。実測された衝突は 899キー・採否反転 426キー。
# 例: ACM Transactions on Applied Perception(SJR)と ACM Symposium on Applied
#     Perception(CORE B)が共に "acm applied perception" になる。
# ---------------------------------------------------------------------------

_JOURNAL_WORDS = re.compile(
    r"\b(journal|transactions|magazine|letters|review|reviews|quarterly|bulletin)\b", re.I)
_CONF_WORDS = re.compile(
    r"\b(conference|symposium|workshop|proceedings|proc|congress|meeting|"
    r"convention|colloquium)\b", re.I)


def venue_type_marker(name: str) -> str:
    """案1: Venue 名から種別マーカーを推定する。'J' / 'C' / ''(不明)。

    ジャーナル語と会議語が両方出るとき(例: "Proceedings of the ACM on
    Human-Computer Interaction" = PACM HCI はジャーナル扱いだが proceedings を含む)は
    **判定不能として '' を返す**。誤ったマーカーを付けると正しい照合まで殺すため、
    曖昧なら両方試す側に倒す。
    """
    has_j = bool(_JOURNAL_WORDS.search(name or ""))
    has_c = bool(_CONF_WORDS.search(name or ""))
    if has_j and not has_c:
        return "J"
    if has_c and not has_j:
        return "C"
    return ""


def typed_key(marker: str, norm: str) -> str:
    return f"{marker}:{norm}"


def candidate_typed_keys(name: str, norm: str) -> list[str]:
    """データ側 Venue に対する照合キー候補。種別不明なら J/C の両方を試す。"""
    if not norm:
        return []
    m = venue_type_marker(name)
    return [typed_key(m, norm)] if m else [typed_key("J", norm), typed_key("C", norm)]


def is_short_key(norm: str, max_tokens: int = 2) -> bool:
    """案3: トークン数が閾値以下の短いキーか。

    短いキー("presence" / "sensors" 等)は正規化一致・fuzzy で誤照合しやすい
    (実例: データの Presence 誌29件が "Annual International Workshop on Presence" に
    吸われて CORE C 判定になった)。短キーでは exact(小文字原題)と ISSN のみ許可する。
    """
    return len(norm.split()) <= max_tokens


def raw_similarity(a: str, b: str) -> float:
    """正規化前の元文字列同士の類似度。"""
    return difflib.SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()


SANITY_THRESHOLD = 0.60        # 案4: 元文字列類似度の下限
CONTAINMENT_THRESHOLD = 0.80   # 案4: 語の包含率の下限(定型句で希釈される場合の救済)

# 包含率の計算から外す純粋な機能語。**種別語や修飾語は落とさない**
# ("international conference" を落とすと、ICSE と PACM SE のような別物まで
#  包含率1.0になってしまう)。
_FILLER = {"of", "the", "on", "and", "in", "for", "a", "an", "to", "at"}


def _content_tokens(s: str) -> set[str]:
    toks = re.findall(r"[a-z0-9]+", (s or "").lower())
    return {t for t in toks
            if t not in _FILLER and not re.fullmatch(r"\d+(?:st|nd|rd|th)?", t)}


def containment(matched_title: str, data_venue: str) -> float:
    """照合先タイトルの語が、データ側 Venue にどれだけ含まれているか。

    元文字列の類似度だけで判定すると、"Proceedings of the 18th ACM International
    Conference on Multimodal Interaction" のような**定型句で薄まった長い Venue 名**が
    正しい照合先 "International Conference on Multimodal Interaction" に対しても
    0.5 程度しか出ず、正当な照合まで棄却してしまう(実測で確認)。
    照合先の語がデータ側に出揃っているかを見れば、この希釈に影響されない。
    """
    # CORE のタイトルは "(was International Conference on Multimodal Interfaces)" や
    # "(ACM)" のような注記を含むことがある。これはデータ側 Venue には現れないので、
    # 残したまま包含率を測ると正しい照合まで閾値割れする。
    m = _content_tokens(re.sub(r"\([^)]*\)", " ", matched_title or ""))
    if not m:
        return 0.0
    return len(m & _content_tokens(data_venue)) / len(m)


def extract_parenthesized_acronym(name: str) -> str:
    """Return text inside the last parentheses if it looks like an acronym,
    e.g. '2010 IEEE VR Conference (VR)' -> 'VR'"""
    m = re.search(r"\(([^)]+)\)\s*$", name.strip())
    if m:
        candidate = m.group(1).strip()
        # Accept if it looks like an acronym: short, mostly uppercase letters/digits
        if re.match(r"^[A-Za-z][A-Za-z0-9 \-]{0,20}$", candidate):
            return candidate
    return ""


def load_core(core_path: Path) -> dict:
    """
    Returns dict: normalized_key -> {original_title, acronym, rank}
    CORE.csv format (no header):
      col0=id, col1=Title, col2=Acronym, col3=Source, col4=Rank, ...
    """
    core: dict = {}
    with core_path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 5:
                continue
            title   = row[1].strip()
            acronym = row[2].strip()
            rank    = row[4].strip()
            if not title:
                continue
            norm = normalize_venue(title)
            entry = {"original_title": title, "acronym": acronym, "rank": rank}
            core[norm] = entry
            if acronym:
                core[acronym.lower()] = entry
            # 案1: 種別マーカー付きキー。CORE は会議ランキングなので既定は 'C'。
            typed = core.setdefault("__typed__", {})
            typed.setdefault(typed_key(venue_type_marker(title) or "C", norm), entry)
    return core


def load_aliases(path: Path) -> dict:
    """venue_aliases.csv を読み、2段の照合辞書を返す。

    著者確認済みの中核会場エイリアス表。**CORE/SJR 照合より先に参照**する
    (誤照合・正規化同名衝突の防止。protocol_changelog.md Rev.6)。
    rank 列は 'CORE A*' / 'SJR Q3' 形式。'MANUAL' 行は文書化のみで照合には使わない。

    返り値: {"exact": {raw.lower(): entry}, "norm": {normalize_venue(raw): entry}}
    照合は exact(生文字列の小文字一致)を優先する。正規化キーはストップワード除去で
    別会場が同一キーになり得るため(例: TAP誌 と SAPシンポジウム は共に
    'acm applied perception')、正規化側で衝突した場合は後勝ちさせず警告して先勝ちを保持。
    """
    aliases = {"exact": {}, "norm": {}}
    if not path.exists():
        return aliases
    with path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        for row in csv.DictReader(f):
            raw = (row.get("Raw venue string") or "").strip()
            canonical = (row.get("Canonical name") or "").strip()
            rank_field = (row.get("CORE/SJR rank") or "").strip()
            if not raw or not rank_field or rank_field.upper().startswith("MANUAL"):
                continue
            parts = rank_field.split(None, 1)
            if len(parts) != 2 or parts[0] not in ("CORE", "SJR"):
                continue
            entry = {"canonical": canonical, "source": parts[0],
                     "rank": parts[1].strip()}
            aliases["exact"][raw.lower()] = entry
            norm = normalize_venue(raw)
            if norm in aliases["norm"] and \
                    aliases["norm"][norm]["canonical"] != canonical:
                print(f"  [WARN] alias正規化キー衝突: '{raw}' (norm='{norm}') は "
                      f"'{aliases['norm'][norm]['canonical']}' と衝突。"
                      "exact一致でのみ照合されます。")
                continue
            aliases["norm"][norm] = entry
    return aliases


def alias_lookup(raw_venue: str, aliases: dict):
    """エイリアス表の2段照合: 生文字列小文字一致 → 正規化一致。無ければ None。"""
    if not aliases:
        return None
    low = raw_venue.strip().lower()
    hit = aliases.get("exact", {}).get(low)
    if hit is not None:
        return hit
    return aliases.get("norm", {}).get(normalize_venue(raw_venue))


def load_sjr(sjr_path: Path) -> dict:
    """
    Returns dict: normalized_key -> {original_title, quartile}
    Also indexes by ISSN (comma-separated) for fast matching.
    scimagojr CSV uses semicolons as separator.
    """
    sjr: dict = {}
    issn_index: dict = {}  # issn -> entry
    with sjr_path.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader, [])
        try:
            title_idx = header.index("Title")
            q_idx     = header.index("SJR Best Quartile")
            issn_idx  = header.index("Issn") if "Issn" in header else -1
        except ValueError:
            print(f"[WARNING] SJR file header not as expected: {header[:6]}")
            return sjr
        for row in reader:
            if len(row) <= max(title_idx, q_idx):
                continue
            title    = row[title_idx].strip().strip('"')
            quartile = row[q_idx].strip().strip('"')
            if not title:
                continue
            norm  = normalize_venue(title)
            entry = {"original_title": title, "quartile": quartile}
            sjr[norm]          = entry
            sjr[title.lower()] = entry
            # 案1: 種別マーカー付きキー。SJR は誌ランキングなので既定は 'J'。
            # setdefault にしているのは、同一キーの「後勝ち上書き」を避けるため
            # (実測の問題: キー 'sensors' が Q1 の Sensors ではなく後行の
            #  Journal of Sensors(Q2)に上書きされ、Q1誌が Q2 として除外され得た)。
            sjr.setdefault("__typed__", {}).setdefault(
                typed_key(venue_type_marker(title) or "J", norm), entry)
            # ISSN index
            if issn_idx >= 0 and issn_idx < len(row):
                issns_raw = row[issn_idx].strip().strip('"')
                for issn in re.split(r"[,\s]+", issns_raw):
                    issn = issn.strip().replace("-", "")
                    if issn:
                        issn_index[issn] = entry
    # Store ISSN index inside sjr under special key
    sjr["__issn_index__"] = issn_index  # type: ignore
    return sjr


_venue_cache: dict[str, tuple] = {}

_sjr_cache: dict[str, tuple] = {}


def _fuzzy_best(norm: str, db: dict, threshold: float):
    """Return (matched_key, score) or (None, 0) via length-pruned fuzzy search."""
    best_score, best_key = 0.0, None
    for k in db:
        max_len = max(len(norm), len(k))
        if max_len == 0:
            continue
        if abs(len(norm) - len(k)) > max_len * (1 - threshold):
            continue
        s = difflib.SequenceMatcher(None, norm, k).ratio()
        if s > best_score:
            best_score, best_key = s, k
    return best_key, best_score


def best_core_match(venue: str, core: dict, threshold: float = 0.82):
    """Cached CORE venue lookup.
    Priority: (1) exact norm, (2) acronym in parentheses, (3) fuzzy.
    """
    if venue in _venue_cache:
        return _venue_cache[venue]
    norm = normalize_venue(venue)
    low  = venue.strip().lower()

    # 1. Exact on normalized name
    if norm and norm in core:
        r = (core[norm]["original_title"], core[norm]["rank"])
        _venue_cache[venue] = r
        return r

    # 2. Exact on lowercase original
    if low in core:
        r = (core[low]["original_title"], core[low]["rank"])
        _venue_cache[venue] = r
        return r

    # 3. Match acronym extracted from parentheses (e.g. "2010 IEEE VR Conference (VR)" -> "VR")
    acronym = extract_parenthesized_acronym(venue)
    if acronym:
        acr_low = acronym.lower()
        if acr_low in core:
            r = (core[acr_low]["original_title"], core[acr_low]["rank"])
            _venue_cache[venue] = r
            return r
        # Also try normalized acronym
        acr_norm = normalize_venue(acronym)
        if acr_norm and acr_norm in core:
            r = (core[acr_norm]["original_title"], core[acr_norm]["rank"])
            _venue_cache[venue] = r
            return r

    # 4. Fuzzy on normalized name (CORE only, ~800 entries, fast enough)
    if norm:
        bk, bs = _fuzzy_best(norm, core, threshold)
        r = (core[bk]["original_title"], core[bk]["rank"]) if bs >= threshold and bk else (None, None)
    else:
        r = (None, None)
    _venue_cache[venue] = r
    return r


def best_sjr_match(venue: str, sjr: dict, issn: str = "", threshold: float = 0.82):
    """Cached SJR lookup: exact title match only (no fuzzy - too slow at 32k entries).
    Falls back to ISSN lookup if provided."""
    cache_key = f"{venue}||{issn}"
    if cache_key in _sjr_cache:
        return _sjr_cache[cache_key]

    issn_index = sjr.get("__issn_index__", {})

    # 1. ISSN lookup (fastest)
    for raw_issn in re.split(r"[,\s]+", issn):
        raw_issn = raw_issn.strip().replace("-", "")
        if raw_issn and raw_issn in issn_index:
            entry = issn_index[raw_issn]
            r = (entry["original_title"], entry["quartile"])
            _sjr_cache[cache_key] = r
            return r

    # 2. Exact normalized title
    norm = normalize_venue(venue)
    low  = venue.strip().lower()
    if norm and norm in sjr and norm != "__issn_index__":
        entry = sjr[norm]
        r = (entry["original_title"], entry["quartile"])
        _sjr_cache[cache_key] = r
        return r
    if low in sjr and low != "__issn_index__":
        entry = sjr[low]
        r = (entry["original_title"], entry["quartile"])
        _sjr_cache[cache_key] = r
        return r

    _sjr_cache[cache_key] = (None, None)
    return None, None


_resolve_cache: dict[str, dict] = {}


def resolve_venue(raw_venue: str, core: dict, sjr: dict, issn: str = "",
                  fuzzy_threshold: float = 0.82) -> dict:
    """Venue → ランキング照合(Rev.12)。

    **案6: exact をリスト横断で fuzzy より常に優先する**照合順序:

        1. CORE exact  (種別キー → 正規化キー → 小文字原題)
        2. SJR  exact  (ISSN → 種別キー → 正規化キー → 小文字原題)
        3. CORE acronym(括弧内略称)
        4. CORE fuzzy  (最後の手段)

    旧実装は「CORE を全段(fuzzy 含む)やってから SJR」だったため、SJR に正確な収載が
    あってもCORE側の低類似 fuzzy が先に成立して奪っていた。最大の実例は
    `Proceedings of the ACM on Human-Computer Interaction`(SJR に正確収載)が
    CORE `Indian Conference on Human-Computer Interaction` に fuzzy 照合された **82件**。

    ガード:
      - 案3 短キーガード: 正規化キーのトークン数 ≤2 では正規化一致・fuzzy を禁止し、
        小文字原題 exact と ISSN のみ許可する。
      - 案4 サニティチェック: 照合成立後に元文字列類似度 ≥ SANITY_THRESHOLD を要求。
        満たさなければ unmatched に落とす(silent failure を顕在化させる)。
        ISSN 一致と小文字原題 exact は同一性が確定しているため対象外。

    戻り値: {"source", "matched_title", "rank", "stage", "rejected"}
            source は "CORE" / "SJR" / None。rejected はガードで棄却した根拠(あれば)。
    """
    ck = f"{raw_venue}||{issn}"
    if ck in _resolve_cache:
        return _resolve_cache[ck]

    def out(source, title, rank, stage, rejected=""):
        r = {"source": source, "matched_title": title, "rank": rank,
             "stage": stage, "rejected": rejected}
        _resolve_cache[ck] = r
        return r

    norm = normalize_venue(raw_venue)
    low = (raw_venue or "").strip().lower()
    short = is_short_key(norm)
    core_typed = core.get("__typed__", {})
    sjr_typed = sjr.get("__typed__", {})
    rejected: list[str] = []

    def sane(entry_title: str, stage: str) -> bool:
        """案4: 照合成立後の安全網。次のどちらかを満たせば通す。

          (a) 元文字列類似度 ≥ SANITY_THRESHOLD
          (b) 照合先の語の包含率 ≥ CONTAINMENT_THRESHOLD かつ照合先が3語以上
              (定型句で希釈された長い Venue 名を正当に救済する。短い照合先で
               包含だけを見ると偶発一致を通すため、語数の下限を課す)
        """
        s = raw_similarity(raw_venue, entry_title)
        if s >= SANITY_THRESHOLD:
            return True
        c = containment(entry_title, raw_venue)
        if c >= CONTAINMENT_THRESHOLD and len(_content_tokens(entry_title)) >= 3:
            return True
        rejected.append(f"{stage}:'{entry_title}'(sim={s:.2f}/cont={c:.2f})")
        return False

    marker = venue_type_marker(raw_venue)

    def is_true_raw_hit(entry: dict) -> bool:
        """`low in db` が本当に「原題(または略称)そのもの」の一致かを検証する。

        core/sjr の辞書は**正規化キーと原題キーを同じ名前空間に混ぜている**ため、
        `low in db` だけでは正規化キーへの偶然の一致を拾ってしまう。
        実例: データ 'Presence' は core['presence'](= "Annual International Workshop
        on Presence" の正規化キー)に当たり、原題一致を装って短キーガードを迂回していた。
        同様に 'Sensors' は sjr['sensors'](= "Journal of Sensors" の正規化キー)に当たる。
        """
        t = (entry.get("original_title") or "").strip().lower()
        a = (entry.get("acronym") or "").strip().lower()
        return low == t or (bool(a) and low == a)

    # --- 1. CORE exact -----------------------------------------------------
    if low in core and is_true_raw_hit(core[low]):
        e = core[low]
        return out("CORE", e["original_title"], e["rank"], "core_exact_raw")
    if norm and not short:
        for k in candidate_typed_keys(raw_venue, norm):
            e = core_typed.get(k)
            if e and sane(e["original_title"], "core_typed"):
                return out("CORE", e["original_title"], e["rank"], "core_exact_typed")
        # 種別が確定しているときは素の正規化キーへフォールバックしない。
        # フォールバックすると種別マーカーの意味が消える(実例: ACM Transactions on
        # Applied Perception(J)が ACM Symposium on Applied Perception(C)に当たる)。
        if not marker:
            e = core.get(norm)
            if e and sane(e["original_title"], "core_norm"):
                return out("CORE", e["original_title"], e["rank"], "core_exact_norm")

    # --- 2. SJR exact ------------------------------------------------------
    issn_index = sjr.get("__issn_index__", {})
    for raw_issn in re.split(r"[,\s]+", issn or ""):
        raw_issn = raw_issn.strip().replace("-", "")
        if raw_issn and raw_issn in issn_index:
            e = issn_index[raw_issn]
            return out("SJR", e["original_title"], e["quartile"], "sjr_issn")
    if low in sjr and low != "__issn_index__" and is_true_raw_hit(sjr[low]):
        e = sjr[low]
        return out("SJR", e["original_title"], e["quartile"], "sjr_exact_raw")
    if norm and not short:
        for k in candidate_typed_keys(raw_venue, norm):
            e = sjr_typed.get(k)
            if e and sane(e["original_title"], "sjr_typed"):
                return out("SJR", e["original_title"], e["quartile"], "sjr_exact_typed")
        if not marker:
            e = sjr.get(norm)
            if e and norm != "__issn_index__" and sane(e["original_title"], "sjr_norm"):
                return out("SJR", e["original_title"], e["quartile"], "sjr_exact_norm")

    # --- 3. CORE acronym ---------------------------------------------------
    #
    # 略称照合では**サニティチェックの向きを逆にする**(2026-08-13 修正)。
    # 通常の照合は「照合先の語がデータ側に出揃っているか」(containment)を見るが、
    # 略称の場合はデータ側の venue 名が公式名より短いのが普通で、この向きだと落ちる。
    # 実例: データ '2015 IEEE virtual reality (VR)' は括弧内略称 (VR) で CORE A* の
    #       'IEEE Conference on Virtual Reality and 3D User Interfaces' に正しく当たるが、
    #       照合先の "3D User Interfaces" がデータ側に無いため cont=0.43 で棄却されていた。
    #       IEEE VR は本サーベイの中核会場であり、この表記で27件が未照合除外されていた。
    # 正しくは「**データ側の語が照合先に含まれるか**」を見る
    # (ieee virtual reality ⊆ IEEE Conference on Virtual Reality and 3D User Interfaces)。
    acronym = extract_parenthesized_acronym(raw_venue)
    if acronym:
        for k in (acronym.lower(), normalize_venue(acronym)):
            e = core.get(k) if k else None
            if not e:
                continue
            title = e["original_title"]
            # 逆向きの包含: データ側 venue 名の語が照合先にどれだけ含まれるか
            back = containment(raw_venue, title)
            if back >= CONTAINMENT_THRESHOLD or sane(title, "core_acronym"):
                return out("CORE", title, e["rank"], "core_acronym")
            rejected.append(f"core_acronym:'{title}'(back_cont={back:.2f})")

    # --- 4. CORE fuzzy(最後の手段) ----------------------------------------
    if norm and not short:
        searchable = {k: v for k, v in core.items() if not k.startswith("__")}
        bk, bs = _fuzzy_best(norm, searchable, fuzzy_threshold)
        if bk and bs >= fuzzy_threshold:
            e = core[bk]
            if sane(e["original_title"], "core_fuzzy"):
                return out("CORE", e["original_title"], e["rank"], "core_fuzzy")

    note = ""
    if short and norm:
        note = f"短キーガード(tokens<=2: '{norm}')"
    if rejected:
        note = (note + " / " if note else "") + "サニティ棄却 " + "; ".join(rejected[:3])
    return out(None, None, None, "unmatched", note)


# ---------------------------------------------------------------------------
# Rev.13: フィルタ層(Phase 1.5) — 取得後に正規化クエリを一律再適用する
#
# 【なぜ必要か】DB ごとに検索の当たり方が違う。実測で判明しているだけでも
#   - 第1波 Scopus は TITLE-ABS-KEY、第2波は TITLE-ABS(scope が違う)
#   - 第1波 IEEE はより広いフィールド指定(1,077件が第2波に現れず、
#     そのうち TA で3群成立するのは 4.7% だけ)
#   - ACM 第2波は Title 検索と Abstract 検索の和集合(フィールド横断の一致を落とす)
# このまま統合すると「どの DB で拾われたか」によって適格性が変わってしまう。
# 取得後に**同じクエリを全レコードへ1回だけ**適用して、この差を吸収する。
# (methodology_decision_Rev7.md 方針3。Zhou et al. 2025 と同じ発想)
#
# 【選定基準より前に置く理由】これは「取得の差を均す処理」であって
# 「適格性で落とす処理」ではない。Venue ランク(Phase 2)やキーワード除外(Phase 3a)
# より前に置き、PRISMA でも別の段として報告する。
#
# 【重複削除より後に置く理由】同じ論文の ACM コピーと Scopus コピーで判定が割れる。
# マージ後の1レコードに対して1回だけ適用する。
#
# 【フェイルセーフ(必須)】要旨が無いレコードは**判定不能であって不適格ではない**。
# タイトルのみで判定すると要旨欠落567件のうち566件が落ちるが、これは中身ではなく
# メタデータ品質による除外であり正当化できない。判定不能は保留し人手へ送る。
# gold set 12件での検証: 本設計での脱落は 0件(タイトルのみ判定だと4件が落ちる)。
# ---------------------------------------------------------------------------

QUERY_CONCEPT_GROUPS_TA = [
    ("G1 没入環境", re.compile(
        r"\b(virtual realit\w*|vr|hmds?|head[- ]mounted displays?"
        r"|virtual environment\w*|immersive virtual)\b", re.I)),
    ("G2 身体表象", re.compile(
        r"\b(avatars?|bod(?:y|ies|ily)|embodiment|embodied)\b", re.I)),
    ("G3 スケール知覚", re.compile(
        r"\b(sizes?|scal\w*|heights?|distances?)\b", re.I)),
]

# 重複グループ間で補完するフィールド(Rev.13)。
#
# **Venue 名(Publication Title)は絶対にマージしない。** DB ごとに表記が違い、
# 「長い方が良い」わけではないため。実際に一度マージしたところ、gold #11 の venue が
# IEEE 表記から Scopus 表記
# ('25th IEEE Conference on Virtual Reality and 3D User Interfaces, VR 2018 - Proceedings')
# に置き換わり、CORE A* に照合できなくなって step2 recall が 3/12 → 2/12 に落ちた。
# Venue 表記の統一はエイリアス表と正規化(Rev.12)の担当であって、マージの仕事ではない。
#
#   MERGE_LONGEST : 値が長い方を採る(切り詰められた要旨があるため)
#   MERGE_IF_EMPTY: 空のときだけ埋める(識別子は上書きしてはならない)
MERGE_LONGEST = ["Abstract Note"]
MERGE_IF_EMPTY = ["DOI", "ISSN"]
MERGE_FIELDS = MERGE_LONGEST + MERGE_IF_EMPTY


def filter_layer_verdict(title: str, abstract: str) -> tuple[str, str]:
    """(verdict, reason) を返す。verdict は 'pass' / 'fail' / 'hold'。

    - 要旨あり: Title+Abstract に3概念群すべてが成立すれば pass、欠ければ fail
    - 要旨なし: **hold**(判定不能。除外せず人手スクリーニングへ)
    """
    abstract = (abstract or "").strip()
    if not abstract:
        return "hold", "要旨なしのため判定不能(フェイルセーフで保留)"
    text = f"{title or ''} {abstract}"
    missing = [name for name, rx in QUERY_CONCEPT_GROUPS_TA if not rx.search(text)]
    if missing:
        return "fail", "概念群が不成立: " + " / ".join(missing)
    return "pass", ""


def compile_exclusions(cats):
    return [(lbl, [(p, re.compile(p, re.IGNORECASE)) for p in pats])
            for lbl, pats in cats]


def screen_keywords(text: str, compiled_cats):
    matched_cats, matched_kws = [], []
    for lbl, cpats in compiled_cats:
        for raw, rx in cpats:
            if rx.search(text):
                if lbl not in matched_cats:
                    matched_cats.append(lbl)
                matched_kws.append(f"{lbl}::{raw}")
    return matched_cats, matched_kws


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

# ---------------------------------------------------------------------------
# Phase 1: Deduplication
# ---------------------------------------------------------------------------

def phase1_dedup(rows: list[dict], fieldnames: list[str],
                 outdir: Path, log_lines: list[str]) -> list[dict]:
    SEP = "=" * 72
    log_lines += [SEP, "  PHASE 1: DEDUPLICATION", SEP, ""]

    title_col = resolve_col(fieldnames, TITLE_ALIASES)
    doi_col   = resolve_col(fieldnames, DOI_ALIASES)
    key_col   = resolve_col(fieldnames, KEY_ALIASES)

    log_lines.append(f"  Input records          : {len(rows):>8,}")
    log_lines.append(f"  Title column           : {title_col!r}")
    log_lines.append(f"  DOI column             : {doi_col!r}")
    log_lines.append(f"  Key column             : {key_col!r}")
    log_lines.append("")

    seen_doi: dict[str, int]   = {}
    seen_title: dict[str, int] = {}
    seen_key: dict[str, int]   = {}

    index_of_kept: dict[int, dict] = {}   # Rev.13: 採用行への参照(フィールド補完用)
    merged_counts: dict[str, int] = {}

    dedup: list[dict] = []
    dup_doi_count   = 0
    dup_title_count = 0
    dup_key_count   = 0

    for i, row in enumerate(rows):
        doi   = (row.get(doi_col,   "") or "").strip().lower() if doi_col   else ""
        title = (row.get(title_col, "") or "").strip().lower() if title_col else ""
        key   = (row.get(key_col,   "") or "").strip()         if key_col   else ""

        dup_reason = ""
        if doi and doi in seen_doi:
            dup_doi_count += 1
            dup_reason = f"Duplicate DOI (first seen at row {seen_doi[doi]})"
        elif key and key in seen_key:
            dup_key_count += 1
            dup_reason = f"Duplicate Key (first seen at row {seen_key[key]})"
        elif title and title in seen_title:
            dup_title_count += 1
            dup_reason = f"Duplicate Title (first seen at row {seen_title[title]})"

        if dup_reason:
            # Rev.13: 重複を捨てる前に、**残す側に欠けているフィールドを補う**。
            # 旧実装は先出コピーをそのまま採用して残りを捨てていたため、
            # 「ACM(要旨なし)が Scopus(要旨あり)より先に並んでいる」というだけの理由で
            # 要旨を捨てていた。実測では欠落7,375件のうち3,439件が、
            # 同じ論文の別コピーに要旨を持っていた(外部API不要で回収できる)。
            # 判定は決定論的(値が空でないもの/より長いものを採る)。
            keep_idx = (seen_doi.get(doi) if doi and doi in seen_doi else
                        seen_key.get(key) if key and key in seen_key else
                        seen_title.get(title))
            if keep_idx is not None:
                kept = index_of_kept.get(keep_idx)
                if kept is not None:
                    for col in MERGE_FIELDS:
                        cur = (kept.get(col) or "").strip()
                        new = (row.get(col) or "").strip()
                        if not new:
                            continue
                        take = (len(new) > len(cur)) if col in MERGE_LONGEST else (not cur)
                        if take:
                            kept[col] = new
                            merged_counts[col] = merged_counts.get(col, 0) + 1
            continue

        if doi:   seen_doi[doi]     = i
        if key:   seen_key[key]     = i
        if title: seen_title[title] = i
        index_of_kept[i] = row
        dedup.append(row)

    removed = len(rows) - len(dedup)
    log_lines.append(f"  Removed by DOI match   : {dup_doi_count:>8,}")
    log_lines.append(f"  Removed by Key match   : {dup_key_count:>8,}")
    log_lines.append(f"  Removed by Title match : {dup_title_count:>8,}")
    if merged_counts:
        log_lines.append("")
        log_lines.append("  --- Field merge from duplicates (Rev.13) ---")
        for col, cnt in sorted(merged_counts.items(), key=lambda x: -x[1]):
            log_lines.append(f"    {col:<22}: {cnt:>8,} 件を重複コピーから補完")
    log_lines.append(f"  Total removed          : {removed:>8,}")
    log_lines.append(f"  Records after dedup    : {len(dedup):>8,}")
    log_lines.append("")

    # Write output
    out_path = outdir / "step1_dedup.csv"
    write_csv(out_path, dedup, fieldnames)
    log_lines.append(f"  Output -> {out_path.name}")
    log_lines.append("")

    # Console
    print(f"\n{'='*60}")
    print(f"  PHASE 1: Deduplication")
    print(f"{'='*60}")
    print(f"  Input     : {len(rows):,}")
    print(f"  Removed   : {removed:,}  (DOI:{dup_doi_count} Key:{dup_key_count} Title:{dup_title_count})")
    print(f"  Remaining : {len(dedup):,}")
    print(f"  Output    : {out_path.name}")

    return dedup

# ---------------------------------------------------------------------------
# Phase 2: CORE Rank Filtering (A / A* only)
# ---------------------------------------------------------------------------

def phase1_5_filter(rows: list[dict], fieldnames: list[str],
                    outdir: Path, log_lines: list[str]) -> list[dict]:
    """Phase 1.5: フィルタ層。取得後に正規化クエリを一律再適用する(Rev.13)。

    設計理由は `filter_layer_verdict` の直上のコメントを参照。
    保留(hold)は**除外しない**。pass と hold を次段へ通す。
    """
    SEP = "=" * 72
    log_lines += [SEP, "  PHASE 1.5: FILTER LAYER (normalized query re-application)",
                  SEP, ""]
    title_col = resolve_col(fieldnames, TITLE_ALIASES)
    abs_col = resolve_col(fieldnames, ABSTRACT_ALIASES)

    kept, dropped = [], []
    n_pass = n_hold = 0
    miss_counter: dict[str, int] = {}
    for row in rows:
        verdict, reason = filter_layer_verdict(
            row.get(title_col, "") if title_col else "",
            row.get(abs_col, "") if abs_col else "")
        row["Filter_Layer"] = verdict
        row["Filter_Layer_Reason"] = reason
        if verdict == "fail":
            dropped.append(row)
            for g in reason.replace("概念群が不成立: ", "").split(" / "):
                miss_counter[g] = miss_counter.get(g, 0) + 1
        else:
            kept.append(row)
            if verdict == "pass":
                n_pass += 1
            else:
                n_hold += 1

    log_lines.append(f"  Input records   : {len(rows):>8,}")
    log_lines.append(f"  Pass (3 groups) : {n_pass:>8,}")
    log_lines.append(f"  Hold (要旨なし) : {n_hold:>8,}   ← 判定不能。除外せず人手へ")
    log_lines.append(f"  Fail (excluded) : {len(dropped):>8,}")
    log_lines.append(f"  Records kept    : {len(kept):>8,}")
    if miss_counter:
        log_lines.append("")
        log_lines.append("  --- 不成立だった概念群(重複計上) ---")
        for g, c in sorted(miss_counter.items(), key=lambda x: -x[1]):
            log_lines.append(f"    {g:<20}: {c:>8,}")
    log_lines.append("")

    out_fields = fieldnames + ["Filter_Layer", "Filter_Layer_Reason"]
    write_csv(outdir / "step1_5_filter_included.csv", kept, out_fields)
    write_csv(outdir / "step1_5_filter_excluded.csv", dropped, out_fields)
    log_lines.append("  Included output -> step1_5_filter_included.csv")
    log_lines.append("  Excluded output -> step1_5_filter_excluded.csv")
    log_lines.append("")

    print(f"\n{'='*60}")
    print(f"  PHASE 1.5: Filter Layer (Rev.13)")
    print(f"{'='*60}")
    print(f"  Input     : {len(rows):,}")
    print(f"  Pass      : {n_pass:,}   Hold(要旨なし): {n_hold:,}")
    print(f"  Excluded  : {len(dropped):,}")
    print(f"  Remaining : {len(kept):,}")
    return kept


def phase2_core(rows: list[dict], fieldnames: list[str],
                core: dict, sjr: dict, outdir: Path, log_lines: list[str],
                aliases: dict | None = None) -> list[dict]:
    SEP = "=" * 72
    log_lines += [SEP, "  PHASE 2: CORE A/A* + SJR Q1 SCREENING", SEP, ""]
    aliases = aliases or {}

    venue_col = resolve_col(fieldnames, VENUE_ALIASES)
    issn_col  = resolve_col(fieldnames, ISSN_ALIASES)
    log_lines.append(f"  Input records   : {len(rows):>8,}")
    log_lines.append(f"  Venue column    : {venue_col!r}")
    log_lines.append(f"  CORE entries    : {len(core):>8,}")
    log_lines.append(f"  SJR entries     : {len(sjr):>8,}")
    n_alias_keys = len(aliases.get("exact", {})) + len(aliases.get("norm", {}))
    log_lines.append(f"  Venue aliases   : {n_alias_keys:>8,} keys")
    log_lines.append("")

    included: list[dict] = []
    excluded: list[dict] = []

    stats: dict[str, int] = defaultdict(int)
    rank_dist: dict[str, int] = defaultdict(int)   # CORE ranks
    sjr_q_dist: dict[str, int] = defaultdict(int)  # SJR quartiles
    unmatched_venues: list[str] = []

    # Rev.12: Match_Stage(どの段で照合したか)と Match_Guard_Note(ガードの棄却理由)を
    # 出力に含める。誤照合が「起きたら見える」状態にするのが構造ガードの本質なので、
    # 監査可能性のために必ず残す。
    _rev12 = ["Match_Stage", "Match_Guard_Note"]
    out_fields_incl = fieldnames + ["Matched_Venue", "Ranking_Source", "CORE_Rank",
                                    "SJR_Quartile"] + _rev12
    out_fields_excl = fieldnames + ["Matched_Venue", "Ranking_Source", "CORE_Rank",
                                    "SJR_Quartile", "Excl_Reason_Phase2"] + _rev12

    for row in rows:
        raw_venue = (row.get(venue_col, "") or "") if venue_col else ""

        # --- Step 0: 著者確認済みエイリアス表(照合より先に参照。誤照合防止) ---
        alias = alias_lookup(raw_venue, aliases)
        if alias is not None:
            row["Match_Stage"]    = "alias"   # Rev.12: 監査のため段を明示する
            row["Matched_Venue"]  = alias["canonical"]
            row["Ranking_Source"] = f"{alias['source']}(alias)"
            row["CORE_Rank"]      = alias["rank"] if alias["source"] == "CORE" else ""
            row["SJR_Quartile"]   = alias["rank"] if alias["source"] == "SJR" else ""
            adopted = (alias["source"] == "CORE" and alias["rank"] in HIGH_RANKS) or \
                      (alias["source"] == "SJR" and alias["rank"] == "Q1")
            if alias["source"] == "CORE":
                rank_dist[alias["rank"]] += 1
            else:
                sjr_q_dist[alias["rank"]] += 1
            if adopted:
                stats["alias_included"] += 1
                row["Excl_Reason_Phase2"] = ""
                included.append(row)
            else:
                stats["alias_low_rank"] += 1
                row["Excl_Reason_Phase2"] = (
                    f"{alias['source']} rank '{alias['rank']}' below threshold "
                    f"(via author-verified alias)")
                excluded.append(row)
            continue

        # --- Step A/B: 照合(Rev.12: exact をリスト横断で fuzzy より優先) ---
        raw_issn = (row.get(issn_col, "") or "") if issn_col else ""
        res = resolve_venue(raw_venue, core, sjr, issn=raw_issn)
        matched_title, rank = (res["matched_title"], res["rank"]) \
            if res["source"] == "CORE" else (None, None)
        row["Match_Stage"] = res["stage"]
        if res["rejected"]:
            row["Match_Guard_Note"] = res["rejected"]
            stats["guard_rejected"] = stats.get("guard_rejected", 0) + 1

        if matched_title is not None:
            row["Matched_Venue"]   = matched_title
            row["Ranking_Source"]  = "CORE"
            row["CORE_Rank"]       = rank
            row["SJR_Quartile"]    = ""
            rank_dist[rank]       += 1
            if rank in HIGH_RANKS:
                stats["core_included"] += 1
                row["Excl_Reason_Phase2"] = ""
                included.append(row)
            else:
                stats["core_low_rank"] += 1
                row["Excl_Reason_Phase2"] = f"CORE Rank '{rank}' < A"
                excluded.append(row)
            continue

        # --- Step B: SJR 側の結果(同じ resolve_venue の戻り値を使う) ---
        sjr_title, quartile = (res["matched_title"], res["rank"]) \
            if res["source"] == "SJR" else (None, None)

        if sjr_title is not None:
            row["Matched_Venue"]   = sjr_title
            row["Ranking_Source"]  = "SJR"
            row["CORE_Rank"]       = ""
            row["SJR_Quartile"]    = quartile
            sjr_q_dist[quartile]  += 1
            if quartile == "Q1":
                stats["sjr_included"] += 1
                row["Excl_Reason_Phase2"] = ""
                included.append(row)
            else:
                stats["sjr_low_rank"] += 1
                row["Excl_Reason_Phase2"] = f"SJR Quartile '{quartile}' is not Q1"
                excluded.append(row)
            continue

        # --- Not found in either DB ---
        stats["unmatched"] += 1
        unmatched_venues.append(raw_venue or "(empty)")
        row["Matched_Venue"]      = ""
        row["Ranking_Source"]     = ""
        row["CORE_Rank"]          = ""
        row["SJR_Quartile"]       = ""
        row["Excl_Reason_Phase2"] = "Venue not found in CORE or SJR"
        excluded.append(row)

    total_included = (stats.get("core_included", 0) + stats.get("sjr_included", 0)
                      + stats.get("alias_included", 0))

    log_lines.append("  --- CORE Rank Distribution ---")
    for r, cnt in sorted(rank_dist.items(), key=lambda x: -RANK_ORDER.get(x[0], 0)):
        log_lines.append(f"    CORE {r:<16}: {cnt:>6,}")
    log_lines.append("")
    log_lines.append("  --- SJR Quartile Distribution ---")
    for q in ["Q1", "Q2", "Q3", "Q4", "-"]:
        cnt = sjr_q_dist.get(q, 0)
        if cnt:
            log_lines.append(f"    SJR  {q:<16}: {cnt:>6,}")
    log_lines.append("")
    log_lines.append(f"  INCLUDED total         : {total_included:>8,}")
    log_lines.append(f"    CORE A/A*            : {stats.get('core_included',0):>8,}")
    log_lines.append(f"    SJR Q1               : {stats.get('sjr_included',0):>8,}")
    log_lines.append(f"    Alias (high rank)    : {stats.get('alias_included',0):>8,}")
    log_lines.append(f"  EXCLUDED total         : {len(excluded):>8,}")
    log_lines.append(f"    CORE low rank (B/C)  : {stats.get('core_low_rank',0):>8,}")
    log_lines.append(f"    SJR Q2/Q3/Q4         : {stats.get('sjr_low_rank',0):>8,}")
    log_lines.append(f"    Alias (low rank)     : {stats.get('alias_low_rank',0):>8,}")
    log_lines.append(f"    Unmatched            : {stats.get('unmatched',0):>8,}")
    log_lines.append("")

    if unmatched_venues:
        log_lines.append("  --- Sample Unmatched Venues (first 30) ---")
        for v in unmatched_venues[:30]:
            log_lines.append(f"    {v}")
        if len(unmatched_venues) > 30:
            log_lines.append(f"    ... and {len(unmatched_venues)-30} more")
        log_lines.append("")

    # Write outputs
    incl_path = outdir / "step2_rank_included.csv"
    excl_path = outdir / "step2_rank_excluded.csv"
    write_csv(incl_path, included, out_fields_incl)
    write_csv(excl_path, excluded, out_fields_excl)

    log_lines.append(f"  Included output -> {incl_path.name}")
    log_lines.append(f"  Excluded output -> {excl_path.name}")
    log_lines.append("")

    # Console
    print(f"\n{'='*60}")
    print(f"  PHASE 2: CORE A/A* + SJR Q1 Screening")
    print(f"{'='*60}")
    print(f"  Input          : {len(rows):,}")
    print(f"  Included total : {total_included:,}")
    print(f"    CORE A/A*    : {stats.get('core_included',0):,}")
    print(f"    SJR Q1       : {stats.get('sjr_included',0):,}")
    print(f"  Excluded       : {len(excluded):,}")
    print(f"    CORE low     : {stats.get('core_low_rank',0):,}")
    print(f"    SJR Q2+      : {stats.get('sjr_low_rank',0):,}")
    print(f"    Unmatched    : {stats.get('unmatched',0):,}")
    print(f"  Incl CSV  : {incl_path.name}")
    print(f"  Excl CSV  : {excl_path.name}")

    return included

# ---------------------------------------------------------------------------
# Phase 3: Keyword Exclusion
# ---------------------------------------------------------------------------

def phase3_keywords(rows: list[dict], fieldnames: list[str],
                    outdir: Path, log_lines: list[str]) -> list[dict]:
    SEP = "=" * 72
    log_lines += [SEP, "  PHASE 3: KEYWORD EXCLUSION", SEP, ""]

    title_col    = resolve_col(fieldnames, TITLE_ALIASES)
    abstract_col = resolve_col(fieldnames, ABSTRACT_ALIASES)
    compiled     = compile_exclusions(EXCLUSION_CATEGORIES)

    log_lines.append(f"  Input records   : {len(rows):>8,}")
    log_lines.append(f"  Title column    : {title_col!r}")
    log_lines.append(f"  Abstract column : {abstract_col!r}")
    log_lines.append("")

    included: list[dict] = []
    excluded: list[dict] = []
    cat_counts: dict[str, int] = defaultdict(int)
    kw_counts:  dict[str, int] = defaultdict(int)

    out_fields_incl = list(fieldnames)
    for f in ["Matched_Venue", "Ranking_Source", "CORE_Rank", "SJR_Quartile"]:
        if f not in out_fields_incl:
            out_fields_incl.append(f)

    out_fields_excl = out_fields_incl + ["KW_Excl_Category", "KW_Excl_Keywords"]

    for row in rows:
        title    = (row.get(title_col,    "") or "") if title_col    else ""
        abstract = (row.get(abstract_col, "") or "") if abstract_col else ""
        haystack = f"{title} {abstract}".lower()

        matched_cats, matched_kws = screen_keywords(haystack, compiled)

        if matched_cats:
            row["KW_Excl_Category"] = " | ".join(matched_cats)
            row["KW_Excl_Keywords"]  = " | ".join(matched_kws)
            excluded.append(row)
            for c in matched_cats:
                cat_counts[c] += 1
            for k in matched_kws:
                kw_counts[k]  += 1
        else:
            included.append(row)

    total = len(rows)
    log_lines.append(f"  Included        : {len(included):>8,}  ({len(included)/total*100:.1f} %)")
    log_lines.append(f"  Excluded        : {len(excluded):>8,}  ({len(excluded)/total*100:.1f} %)")
    log_lines.append("")
    log_lines.append("  --- By Category ---")
    for lbl, _ in EXCLUSION_CATEGORIES:
        n = cat_counts.get(lbl, 0)
        log_lines.append(f"    {n:>6,}  {lbl}")
    log_lines.append("")
    log_lines.append("  --- By Keyword (top hits) ---")
    for lbl, pats in EXCLUSION_CATEGORIES:
        log_lines.append(f"  +-- {lbl}")
        kw_rows = [(p, kw_counts.get(f"{lbl}::{p}", 0)) for p in pats]
        for p, cnt in sorted(kw_rows, key=lambda x: -x[1]):
            if cnt > 0:
                log_lines.append(f"  |  {cnt:>6,}  {p}")
        log_lines.append("  |")
    log_lines.append("")
    log_lines.append("  --- Silent Patterns (zero hits) ---")
    for lbl, pats in EXCLUSION_CATEGORIES:
        silent = [p for p in pats if kw_counts.get(f"{lbl}::{p}", 0) == 0]
        if silent:
            log_lines.append(f"  {lbl}")
            for p in silent:
                log_lines.append(f"    {p}")

    # Write outputs
    incl_path = outdir / "step3_kw_included.csv"
    excl_path = outdir / "step3_kw_excluded.csv"
    write_csv(incl_path, included, out_fields_incl)
    write_csv(excl_path, excluded, out_fields_excl)

    log_lines.append("")
    log_lines.append(f"  Included output -> {incl_path.name}")
    log_lines.append(f"  Excluded output -> {excl_path.name}")
    log_lines.append("")

    # Console
    print(f"\n{'='*60}")
    print(f"  PHASE 3: Keyword Exclusion")
    print(f"{'='*60}")
    print(f"  Input     : {total:,}")
    print(f"  Included  : {len(included):,}  ({len(included)/total*100:.1f} %)")
    print(f"  Excluded  : {len(excluded):,}  ({len(excluded)/total*100:.1f} %)")
    for lbl, _ in EXCLUSION_CATEGORIES:
        n = cat_counts.get(lbl, 0)
        print(f"    {n:>6,}  {lbl}")
    print(f"  Incl CSV  : {incl_path.name}")
    print(f"  Excl CSV  : {excl_path.name}")

    return included

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description="3-Phase PRISMA Screening Pipeline")
    parser.add_argument("--input",  "-i", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--core",   "-c", type=Path, default=DEFAULT_CORE)
    parser.add_argument("--sjr",    "-s", type=Path, default=DEFAULT_SJR)
    parser.add_argument("--aliases", "-a", type=Path, default=DEFAULT_ALIASES,
                        help="著者確認済み Venue エイリアス表(照合より先に参照)")
    parser.add_argument("--outdir", "-o", type=Path, default=DEFAULT_OUTDIR)
    args = parser.parse_args(argv)

    if not args.input.exists():
        sys.exit(f"[ERROR] Input not found: {args.input}")
    if not args.core.exists():
        sys.exit(f"[ERROR] CORE file not found: {args.core}")
    if not args.sjr.exists():
        sys.exit(f"[ERROR] SJR file not found: {args.sjr}")

    args.outdir.mkdir(parents=True, exist_ok=True)
    log_path = args.outdir / "pipeline_log.txt"
    log_lines: list[str] = [
        "=" * 72,
        "  PRISMA 3-Phase Screening Pipeline",
        f"  Input : {args.input}",
        f"  CORE  : {args.core}",
        "=" * 72,
        "",
    ]

    print(f"\n{'='*60}")
    print(f"  PRISMA Pipeline  |  {args.input.name}")
    print(f"{'='*60}")

    # Load input
    print(f"  Reading {args.input.name} ...")
    rows: list[dict] = []
    fieldnames: list[str] = []
    with args.input.open(encoding="utf-8-sig", newline="", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    print(f"  Loaded {len(rows):,} records, {len(fieldnames)} columns.")

    # Load CORE
    print(f"  Loading CORE rankings from {args.core.name} ...")
    core = load_core(args.core)
    print(f"  CORE entries loaded: {len(core):,}")

    # Load SJR
    print(f"  Loading SJR rankings from {args.sjr.name} ...")
    sjr = load_sjr(args.sjr)
    print(f"  SJR  entries loaded: {len(sjr):,}")

    # Load venue aliases (author-verified; consulted BEFORE CORE/SJR matching)
    aliases = load_aliases(args.aliases)
    n_alias_keys = len(aliases.get("exact", {})) + len(aliases.get("norm", {}))
    print(f"  Venue aliases loaded: {n_alias_keys:,} keys "
          f"({args.aliases.name if args.aliases.exists() else 'not found'})")

    # ── Phase 1 ──────────────────────────────────────────────
    after_p1 = phase1_dedup(rows, fieldnames, args.outdir, log_lines)

    # ── Phase 1.5(Rev.13): 取得の差を均す。選定基準(P2/P3)より前に置く ──
    after_p15 = phase1_5_filter(after_p1, fieldnames, args.outdir, log_lines)
    fieldnames_f = fieldnames + ["Filter_Layer", "Filter_Layer_Reason"]

    # ── Phase 2 ──────────────────────────────────────────────
    after_p2 = phase2_core(after_p15, fieldnames_f, core, sjr, args.outdir, log_lines,
                           aliases=aliases)

    # ── Phase 3 ──────────────────────────────────────────────
    after_p3 = phase3_keywords(after_p2, fieldnames_f, args.outdir, log_lines)

    # Summary
    SEP = "=" * 72
    log_lines += [
        SEP, "  PIPELINE SUMMARY", SEP, "",
        f"  Original records   : {len(rows):>8,}",
        f"  After dedup (P1)   : {len(after_p1):>8,}  (-{len(rows)-len(after_p1):,})",
        f"  After filter (P1.5): {len(after_p15):>8,}  (-{len(after_p1)-len(after_p15):,})",
        f"  After CORE  (P2)   : {len(after_p2):>8,}  (-{len(after_p15)-len(after_p2):,})",
        f"  After keywords (P3): {len(after_p3):>8,}  (-{len(after_p2)-len(after_p3):,})",
        "",
        "  Output files:",
        f"    step1_dedup.csv",
        f"    step2_rank_included.csv  (CORE A/A* + SJR Q1)",
        f"    step2_rank_excluded.csv",
        f"    step3_kw_included.csv   <- 最終候補",
        f"    step3_kw_excluded.csv",
        f"    pipeline_log.txt",
        "",
    ]

    with log_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print(f"\n{'='*60}")
    print(f"  PIPELINE SUMMARY")
    print(f"{'='*60}")
    print(f"  Original   : {len(rows):,}")
    print(f"  → Dedup    : {len(after_p1):,}")
    print(f"  → CORE A/A*: {len(after_p2):,}")
    print(f"  → Keywords : {len(after_p3):,}  ← 最終候補")
    print(f"\n  Log: {log_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
