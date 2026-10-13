"""Phase 4 用の全文 PDF を、合法的に取得できる範囲(OA)で集める。

使い方:
    python -X utf8 scripts/fetch_fulltext.py --targets <ids.json>

入力  : ids.json(record_id の配列)と screening/stage1/assignment.csv(DOI・タイトル)
出力  : fulltext/pdf/<record_id>.pdf        … 原本(1論文1ファイル)
        fulltext/by_reviewer/<人>/<record_id>.pdf … 担当者ごとのコピー
        fulltext/manifest.csv               … 取得状況・出所・担当ペア

取得元は OA の配布元のみ: OpenAlex(DOI → OA 場所の PDF URL)→ Semantic Scholar(openAccessPdf。
arXiv・機関リポジトリのコピーを含む)の順に試す。PMC / Europe PMC の PDF は自動取得を 403 で拒否するため使わない。購読誌の有料壁や出版社のボット対策は回避しない
(UA の偽装もしない。403 を返す出版社の OA 論文は手動取得に回る)。
取得できなかった論文は manifest.csv の status=missing に残し、学内ライセンスなどで手動取得する。
担当ペアは record_id の md5 で3ブロックに決定論的に分ける(仮割当。Phase 4 開始時に確定する)。
"""
import argparse
import csv
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "SurveyProtocol-fulltext-fetch"}
PAIRS = {0: ("author", "kataoka"), 1: ("author", "watanabe"), 2: ("kataoka", "watanabe")}
MAX_BYTES = 60 * 1024 * 1024


def get(url: str, timeout: int = 40) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read(MAX_BYTES)


def download_pdf(url: str, dest: Path) -> bool:
    """curl で取得する(Windows の証明書ストアを使うため。TLS 検証は有効のまま)。"""
    tmp = dest.with_suffix(".part")
    cmd = ["curl", "-sS", "-L", "--fail", "-m", "90", "-A", UA["User-Agent"],
           "--max-filesize", str(MAX_BYTES), "-o", str(tmp), url]
    if subprocess.run(cmd, capture_output=True).returncode == 0 and tmp.read_bytes()[:5] == b"%PDF-":
        tmp.replace(dest)
        return True
    tmp.unlink(missing_ok=True)
    return False


def norm_title(t: str) -> str:
    return re.sub(r"[^0-9a-z]+", " ", t.lower()).strip()


def same_title(a: str, b: str) -> bool:
    return difflib.SequenceMatcher(None, norm_title(a), norm_title(b)).ratio() >= 0.9


def openalex_pdf_urls(doi: str, title: str) -> list[str]:
    sel = "select=open_access,best_oa_location,locations"
    work = None
    if doi:
        url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}?{sel}"
        try:
            work = json.loads(get(url))
        except urllib.error.HTTPError as e:
            if e.code != 404:  # DOI が OpenAlex に無い(404)ときだけタイトル検索へ落とす
                raise
    if work is None:
        # 検索の先頭は無関係な論文でも返るため、タイトルがほぼ一致するものだけを採る
        # (照合しないと別論文の PDF を record_id の名前で保存してしまう)
        if len(norm_title(title)) < 20:
            return []
        q = urllib.parse.quote(title)
        res = json.loads(get(f"https://api.openalex.org/works?search={q}&per-page=5"
                             f"&{sel},display_name"))
        work = next((w for w in res.get("results") or []
                     if same_title(title, w.get("display_name") or "")), None)
        if not work:
            return []
    urls = []
    best = work.get("best_oa_location") or {}
    for loc in [best] + (work.get("locations") or []):
        u = (loc or {}).get("pdf_url")
        if u and u not in urls:
            urls.append(u)
    return urls


def semantic_scholar_pdf_urls(doi: str) -> list[str]:
    """Semantic Scholar の openAccessPdf(arXiv・機関リポジトリのコピーを含む)。"""
    if not doi:
        return []
    url = (f"https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi)}"
           "?fields=openAccessPdf")
    try:
        u = (json.loads(get(url)).get("openAccessPdf") or {}).get("url")
    except urllib.error.HTTPError as e:
        if e.code in (404, 429):  # 未収載 / 無認証のレート制限は「見つからない」扱い
            return []
        raise
    return [u] if u else []


def candidate_urls(doi: str, title: str) -> list[tuple[str, str]]:
    """(経路, URL) を優先順に返す。1経路の API 失敗で他の経路を止めない。"""
    out, errors = [], []
    for name, fn in [("openalex", lambda: openalex_pdf_urls(doi, title)),
                     ("semanticscholar", lambda: semantic_scholar_pdf_urls(doi))]:
        try:
            out += [(name, u) for u in fn() if u not in {x for _, x in out}]
        except Exception as e:  # ネットワーク/API 失敗は記録して次の経路へ
            errors.append(f"{name}: {type(e).__name__}")
    if not out and errors:
        raise RuntimeError("; ".join(errors))
    return out


def pair_of(record_id: str) -> tuple[str, str]:
    return PAIRS[int(hashlib.md5(record_id.encode()).hexdigest(), 16) % 3]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", required=True)
    args = ap.parse_args()
    ids = json.loads(Path(args.targets).read_text(encoding="utf-8"))
    asg = {r["record_id"]: r for r in csv.DictReader(
        (ROOT / "screening" / "stage1" / "assignment.csv").open(encoding="utf-8-sig", newline=""))}

    out = ROOT / "fulltext"
    (out / "pdf").mkdir(parents=True, exist_ok=True)
    # 再実行時に取得済み PDF の出所 URL を "cached" で上書きしないよう、前回の manifest から引き継ぐ
    prev_src = {}
    if (out / "manifest.csv").exists():
        prev_src = {r["record_id"]: r["source"] for r in csv.DictReader(
            (out / "manifest.csv").open(encoding="utf-8-sig", newline="")) if r["status"] == "ok"}
    rows = []
    for n, rid in enumerate(ids, 1):
        a = asg[rid]
        doi, title = a["doi"].strip(), a["title"].strip()
        dest = out / "pdf" / f"{rid}.pdf"
        source, status = "", "missing"
        if dest.exists() and dest.read_bytes()[:5] == b"%PDF-":
            status, source = "ok", prev_src.get(rid) or "cached"
        else:
            try:
                urls = candidate_urls(doi, title)
                for attempt in range(2):  # 一時的な失敗(タイムアウト等)に備えて1回だけ再試行
                    for _, u in urls:
                        if download_pdf(u, dest):
                            status, source = "ok", u
                            break
                    if status == "ok" or not urls:
                        break
                    time.sleep(2)
            except Exception as e:  # 全経路の API が失敗した場合は missing のまま記録する
                source = f"error: {e}"
            time.sleep(1.0)  # Semantic Scholar の無認証レート制限(約1件/秒)に合わせる
        p = pair_of(rid)
        if status == "ok":
            for who in p:
                d = out / "by_reviewer" / who
                d.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(dest, d / f"{rid}.pdf")
        rows.append({"record_id": rid, "pair": "×".join(p), "status": status,
                     "doi": doi, "title": title, "source": source})
        print(f"[{n}/{len(ids)}] {rid} {status}", flush=True)

    with (out / "manifest.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    write_manual_list(rows, out / "manual_fetch.md")
    ok = sum(r["status"] == "ok" for r in rows)
    print(f"取得 {ok} / {len(rows)} 件。manifest: {out / 'manifest.csv'}")
    print(f"手動取得リスト: {out / 'manual_fetch.md'}")


PUBLISHERS = {"10.1109": "IEEE", "10.1145": "ACM", "10.1016": "Elsevier", "10.1007": "Springer",
              "10.1177": "SAGE", "10.1162": "MIT Press", "10.3390": "MDPI", "10.3389": "Frontiers",
              "10.1080": "Taylor & Francis", "10.1111": "Wiley", "10.1002": "Wiley"}


def write_manual_list(rows: list[dict], path: Path) -> None:
    """status=missing の論文を出版社別のチェックリストにする(manifest.csv から再生成される写し)。"""
    groups: dict[str, list[dict]] = {}
    for r in rows:
        if r["status"] != "ok":
            key = PUBLISHERS.get(r["doi"].split("/")[0], "その他") if r["doi"] else "DOI なし(書誌の確認が先)"
            groups.setdefault(key, []).append(r)
    lines = ["# Phase 4 手動取得リスト", "",
             "`scripts/fetch_fulltext.py` が manifest.csv から自動生成する。手で編集しない。",
             "取得した PDF は `fulltext/pdf/<record_id>.pdf` に置き、スクリプトを再実行すると担当者フォルダへ配られる。",
             "", f"未取得 {sum(map(len, groups.values()))} 件", ""]
    for key, rs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        lines += [f"## {key}({len(rs)} 件)", ""]
        for r in rs:
            link = f"[{r['doi']}](https://doi.org/{r['doi']})" if r["doi"] else "DOI なし"
            lines.append(f"- [ ] `{r['record_id']}` {r['title']} — {link}({r['pair']})")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
