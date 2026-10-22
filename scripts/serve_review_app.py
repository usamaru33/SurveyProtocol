#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""全文評価の閲覧アプリを、同じ Wi-Fi 内のスマホ・タブレットから使えるように PC で配信する。

  python -X utf8 scripts/serve_review_app.py --id author

表示された URL(`http://<PC の IP>:8765/<合言葉>/review_author.html`)をスマホで開く。
  - 配るのは、その評価者の review_<id>.html・ja_<id>.js(日本語要約)・pdf/ だけ。ほかのファイルは出さない。
  - URL に合言葉が入っている。知らない人は開けない(同じ Wi-Fi でも)。
  - アプリの入力は、変更のたびに PC の progress_<id>.json へ自動で保存される(スマホ側の保存操作は不要)。
    スマホのブラウザを替えても、同じ URL を開けば PC 側の保存が引き継がれる。
  - 論文 PDF(著作物)をネットに公開しないこと。この配信は同じ Wi-Fi の中だけで使う。Ctrl+C で止める。
初回は Windows ファイアウォールの許可ダイアログが出る。「プライベート ネットワーク」を許可する。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import socket
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from make_screening_sheets import REVIEWERS  # noqa: E402

PHASE4 = _HERE.parent / "screening" / "phase4"
MAX_BODY = 8 * 1024 * 1024
FULLTEXT = _HERE.parent / "fulltext"
RID = re.compile(r"^R[0-9a-f]{6,12}$")


def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))          # 実際には送信しない。経路の選択だけ
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def make_handler(root: Path, who: str, token: str):
    html_name = f"review_{who}.html"
    prog = root / f"progress_{who}.json"
    reqf = root / "translate_requests.json"           # 手法の和訳依頼(Claude が処理して fulltext/method_ja/ に書く)

    def read_json(f: Path):
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def mstate(rid: str) -> dict:
        m = read_json(FULLTEXT / "method" / f"{rid}.json")
        ja = read_json(FULLTEXT / "method_ja" / f"{rid}.json")
        reqs = read_json(reqf) or []
        return {"has_sections": bool(m and m.get("sections")), "chars": (m or {}).get("chars", 0),
                "ja": ja, "requested": rid in reqs}

    class H(BaseHTTPRequestHandler):
        server_version = "review"

        def log_message(self, fmt, *a):             # PDF の取得ログで埋まらないよう、保存だけ表示
            if self.command == "POST":
                sys.stderr.write("[保存] %s\n" % (fmt % a))

        def _rel(self):
            path = unquote(urlsplit(self.path).path)
            pre = f"/{token}/"
            if not path.startswith(pre):
                return None
            return path[len(pre):]

        def _send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def do_GET(self):
            rel = self._rel()
            if rel is None:
                return self._send(404, "not found".encode())
            if rel in ("", html_name):
                f, ct = root / html_name, "text/html; charset=utf-8"
            elif rel == f"ja_{who}.js":                 # AI の日本語要約・本文(あれば)
                f, ct = root / rel, "text/javascript; charset=utf-8"
            elif rel.startswith("mstate/") and RID.match(rel[7:]):   # 手法の和訳の状態(和訳があれば本文も)
                return self._send(200, json.dumps(mstate(rel[7:]), ensure_ascii=False).encode(), "application/json; charset=utf-8")
            elif rel == "progress.json":
                f, ct = prog, "application/json; charset=utf-8"
            elif rel.startswith("pdf/") and rel.lower().endswith(".pdf") and "/" not in rel[4:] and ".." not in rel:
                f, ct = root / "pdf" / rel[4:], "application/pdf"
            else:
                return self._send(404, "not found".encode())
            if not f.is_file():
                return self._send(404, "not found".encode())
            self._send(200, f.read_bytes(), ct)

        do_HEAD = do_GET

        def do_POST(self):
            if self._rel() == "mrequest":
                n = int(self.headers.get("Content-Length") or 0)
                try:
                    rid = json.loads(self.rfile.read(min(n, 1024)).decode("utf-8")).get("id", "")
                except ValueError:
                    return self._send(400, "json".encode())
                if not RID.match(str(rid)):
                    return self._send(400, "id".encode())
                reqs = read_json(reqf) or []
                if rid not in reqs:
                    reqs.append(rid)
                    reqf.write_text(json.dumps(reqs, ensure_ascii=False, indent=1), encoding="utf-8")
                self.log_message("和訳依頼 %s(待ち %s 件)", rid, len(reqs))
                return self._send(200, b"ok")
            if self._rel() != "save":
                return self._send(404, "not found".encode())
            n = int(self.headers.get("Content-Length") or 0)
            if n <= 0 or n > MAX_BODY:
                return self._send(413, "size".encode())
            try:
                data = json.loads(self.rfile.read(n).decode("utf-8"))
            except ValueError:
                return self._send(400, "json".encode())
            if not isinstance(data, dict) or data.get("format") != "phase4-progress" or data.get("sheet") != who:
                return self._send(400, "format/sheet".encode())
            fd, tmp = tempfile.mkstemp(dir=root, suffix=".tmp")      # 途中で切れても壊れないよう、書いてから置き換える
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=1)
            os.replace(tmp, prog)
            c = data.get("counts") or {}
            self.log_message("判定 %s/%s", c.get("done", "?"), c.get("total", "?"))
            self._send(200, b"ok")

    return H


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", required=True, choices=list(REVIEWERS))
    ap.add_argument("--dir", type=Path, default=PHASE4)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--token", default="", help="URL の合言葉(省略で毎回ランダム。同じ URL を使い回したいときに指定)")
    args = ap.parse_args()
    root = args.dir / args.id
    if not (root / f"review_{args.id}.html").exists():
        sys.exit(f"[ERROR] {root / ('review_' + args.id + '.html')} が無い。先に make_fulltext_review_app.py --id {args.id}")
    token = args.token or secrets.token_urlsafe(6)
    srv = ThreadingHTTPServer(("0.0.0.0", args.port), make_handler(root, args.id, token))
    ip = lan_ip()
    print(f"[OK] {REVIEWERS[args.id]} 用に配信中。スマホ(同じ Wi-Fi)でこの URL を開く:\n")
    print(f"    http://{ip}:{args.port}/{token}/review_{args.id}.html\n")
    print(f"  保存先: {root / ('progress_' + args.id + '.json')}(変更のたびに自動)")
    print("  止めるときは Ctrl+C。PDF を含むので、この URL を他人に渡さない。")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[停止]")


if __name__ == "__main__":
    main()
