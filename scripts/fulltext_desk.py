"""Phase 4 の手動取得を進める作業用ツール(ローカルの Web ページ + 受け箱の自動仕分け)。

使い方:
    python -X utf8 scripts/fulltext_desk.py                       # fulltext/inbox/ を監視
    python -X utf8 scripts/fulltext_desk.py --inbox ~/Downloads   # ダウンロードフォルダを監視

ブラウザで http://127.0.0.1:8765/ が開く。
  1. 「次を開く」(Enter)で出版社のページが新しいタブで開く。PDF を受け箱に保存する
  2. 受け箱は2秒ごとに監視され、保存された PDF は sort_fulltext_inbox.process() で中身を照合して
     record_id に振り分けられる(manifest.csv・manual_fetch.md も更新)。画面の行が ✅ になり次へ進む
  3. 照合できなかった PDF は画面下に出るので、論文を選んで割り当てる

ダウンロード自体は人がブラウザで行う。出版社サイトへの自動アクセスはこのツールは一切しない
(一括・自動ダウンロードは購読契約の規約違反になるため)。
--inbox にダウンロードフォルダなど既存のフォルダを指定した場合は、起動後に保存された PDF だけを扱う。
"""
import argparse
import json
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from fetch_fulltext import PUBLISHERS
from sort_fulltext_inbox import OUT, inbox_pdfs, load_manifest, process

LOCK = threading.Lock()
STATE = {"events": [], "left": {}}  # left: ファイル名 → 理由(受け箱に残っている未照合ファイル)


def publisher(doi: str) -> str:
    return PUBLISHERS.get(doi.split("/")[0], "その他") if doi else "DOI なし"


def log(kind: str, text: str) -> None:
    STATE["events"].insert(0, {"t": time.strftime("%H:%M:%S"), "kind": kind, "text": text})
    del STATE["events"][30:]


class Watcher(threading.Thread):
    """受け箱を監視し、サイズが落ち着いた PDF(書き込み途中でないもの)を仕分ける。"""

    def __init__(self, inbox: Path, only_new: bool):
        super().__init__(daemon=True)
        self.inbox, self.since = inbox, (time.time() if only_new else 0.0)
        self.seen: dict[str, tuple] = {}  # ファイル名 → 前回の (サイズ, 更新時刻)
        self.judged: dict[str, tuple] = {}  # 未照合と判定済みのファイル → そのときの (サイズ, 更新時刻)

    def candidates(self) -> list[Path]:
        ready = []
        for p in inbox_pdfs(self.inbox):
            st = p.stat()
            if st.st_mtime < self.since:
                continue
            sig = (st.st_size, st.st_mtime)
            stable = self.seen.get(p.name) == sig  # 2回続けて同じなら書き込み完了とみなす
            self.seen[p.name] = sig
            if stable and self.judged.get(p.name) != sig:
                ready.append(p)
        return ready

    def run(self) -> None:
        while True:
            try:
                ready = self.candidates()
                if ready:
                    with LOCK:
                        taken, left, rows = process(ready)
                        by_id = {r["record_id"]: r for r in rows}
                        for name, rid, how in taken:
                            STATE["left"].pop(name, None)
                            log("ok", f"{name} → {rid}({how}){by_id[rid]['title'][:70]}")
                        for name, why in left:
                            p = self.inbox / name
                            if p.exists():
                                st = p.stat()
                                self.judged[name] = (st.st_size, st.st_mtime)
                            if STATE["left"].get(name) != why:
                                log("warn", f"{name}: {why}")
                            STATE["left"][name] = why
                with LOCK:  # 手で消された未照合ファイルを一覧から外す
                    for name in [n for n in STATE["left"] if not (self.inbox / n).exists()]:
                        STATE["left"].pop(name)
            except Exception as e:  # 監視は止めない
                log("warn", f"仕分けでエラー: {type(e).__name__}: {e}")
            time.sleep(2)


def make_handler(inbox: Path):
    page = (Path(__file__).with_name("fulltext_desk.html")).read_text(encoding="utf-8")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):  # アクセスログで端末を埋めない
            pass

        def send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def json(self, obj, code: int = 200) -> None:
            self.send(code, json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8")

        def do_GET(self):
            if self.path == "/":
                self.send(200, page.encode(), "text/html; charset=utf-8")
            elif self.path == "/api/state":
                with LOCK:
                    rows = load_manifest()
                    self.json({
                        "inbox": str(inbox),
                        "records": [{"id": r["record_id"], "title": r["title"], "doi": r["doi"],
                                     "pair": r["pair"], "ok": r["status"] == "ok",
                                     "manual": r["source"].startswith("manual:"),
                                     "publisher": publisher(r["doi"])} for r in rows],
                        "left": [{"file": k, "why": v} for k, v in STATE["left"].items()],
                        "events": STATE["events"],
                    })
            else:
                self.send(404, b"not found", "text/plain")

        def do_POST(self):
            # 他サイトのページから localhost へ POST されても受け付けない
            if self.headers.get("Origin") not in (None, f"http://{self.headers.get('Host')}"):
                return self.json({"error": "origin"}, 403)
            if self.path != "/api/assign":
                return self.json({"error": "not found"}, 404)
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            name, rid = Path(body.get("file", "")).name, body.get("id", "")
            pdf = inbox / name
            if not name or not pdf.exists():
                return self.json({"error": "受け箱にそのファイルがありません"}, 400)
            with LOCK:
                try:
                    taken, left, _ = process([pdf], {name: rid})
                except ValueError as e:
                    return self.json({"error": str(e)}, 400)
                if taken:
                    STATE["left"].pop(name, None)
                    log("ok", f"{name} → {rid}(手動指定)")
                    return self.json({"ok": True})
                return self.json({"error": left[0][1] if left else "割り当てられませんでした"}, 400)

    return Handler


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", type=Path, default=OUT / "inbox")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()
    inbox = args.inbox.expanduser().resolve()
    inbox.mkdir(parents=True, exist_ok=True)
    only_new = inbox != (OUT / "inbox").resolve()

    Watcher(inbox, only_new).start()
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(inbox))
    url = f"http://127.0.0.1:{args.port}/"
    print(f"作業用ツール: {url}")
    print(f"受け箱: {inbox}{'(起動後に保存された PDF だけを扱う)' if only_new else ''}")
    print("終了は Ctrl+C")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
