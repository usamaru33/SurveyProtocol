"""Phase 4 用の全文 PDF を、合法的に取得できる範囲(OA)で集める。

使い方:
    python -X utf8 scripts/fetch_fulltext.py --targets <ids.json>

入力  : ids.json(record_id の配列)と screening/assignment.csv(DOI・タイトル)
出力  : fulltext/pdf/<record_id>.pdf        … 原本(1論文1ファイル)
        fulltext/by_reviewer/<人>/<record_id>.pdf … 担当者ごとのコピー
        fulltext/manifest.csv               … 取得状況・出所・担当ペア

取得元は OpenAlex(DOI → OA 場所の PDF URL)のみ。購読誌の有料壁は回避しない。
取得できなかった論文は manifest.csv の status=missing に残し、学内ライセンスなどで手動取得する。
担当ペアは record_id の md5 で3ブロックに決定論的に分ける(仮割当。Phase 4 開始時に確定する)。
"""
import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import time
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


def openalex_pdf_urls(doi: str, title: str) -> list[str]:
    sel = "select=open_access,best_oa_location,locations"
    if doi:
        url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}?{sel}"
        work = json.loads(get(url))
    else:
        q = urllib.parse.quote(title)
        res = json.loads(get(f"https://api.openalex.org/works?search={q}&per-page=1&{sel}"))
        work = (res.get("results") or [None])[0]
        if not work:
            return []
    urls = []
    best = work.get("best_oa_location") or {}
    for loc in [best] + (work.get("locations") or []):
        u = (loc or {}).get("pdf_url")
        if u and u not in urls:
            urls.append(u)
    return urls


def pair_of(record_id: str) -> tuple[str, str]:
    return PAIRS[int(hashlib.md5(record_id.encode()).hexdigest(), 16) % 3]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", required=True)
    args = ap.parse_args()
    ids = json.loads(Path(args.targets).read_text(encoding="utf-8"))
    asg = {r["record_id"]: r for r in csv.DictReader(
        (ROOT / "screening" / "assignment.csv").open(encoding="utf-8-sig", newline=""))}

    out = ROOT / "fulltext"
    (out / "pdf").mkdir(parents=True, exist_ok=True)
    rows = []
    for n, rid in enumerate(ids, 1):
        a = asg[rid]
        doi, title = a["doi"].strip(), a["title"].strip()
        dest = out / "pdf" / f"{rid}.pdf"
        source, status = "", "missing"
        if dest.exists() and dest.read_bytes()[:5] == b"%PDF-":
            status, source = "ok", "cached"
        else:
            try:
                for u in openalex_pdf_urls(doi, title):
                    if download_pdf(u, dest):
                        status, source = "ok", u
                        break
            except Exception as e:  # ネットワーク/API 失敗は missing のまま記録する
                source = f"error: {type(e).__name__}"
            time.sleep(0.3)
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
    ok = sum(r["status"] == "ok" for r in rows)
    print(f"取得 {ok} / {len(rows)} 件。manifest: {out / 'manifest.csv'}")


if __name__ == "__main__":
    main()
