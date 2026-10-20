"""Markdown を PDF にする(markdown → HTML → Chrome/Edge のヘッドレス印刷)。

使い方:  python -X utf8 scripts/md_to_pdf.py docs/reference/mtg_taxonomy_phase4.md [...]
出力は入力と同じ場所に <名前>.pdf。ブラウザ(Chrome か Edge)が必要。
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
CSS = """
@page { size: A4; margin: 16mm 14mm; }
body { font-family: 'Yu Gothic UI','Meiryo','Noto Sans CJK JP',sans-serif; font-size: 10pt; line-height: 1.6; color:#111; }
h1 { font-size: 17pt; border-bottom: 2px solid #333; padding-bottom: 4px; margin-top: 1.4em; }
h2 { font-size: 13pt; border-bottom: 1px solid #999; padding-bottom: 2px; margin-top: 1.3em; }
h3 { font-size: 11pt; }
table { border-collapse: collapse; width: 100%; margin: .6em 0; font-size: 9pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #888; padding: 3px 6px; vertical-align: top; }
th { background: #eee; }
code { background: #f2f2f2; padding: 0 3px; font-size: 9pt; }
pre { background: #f6f6f6; padding: 6px; overflow-wrap: anywhere; white-space: pre-wrap; }
blockquote { border-left: 4px solid #bbb; margin-left: 0; padding-left: 10px; color:#444; }
hr { border: 0; border-top: 1px solid #ccc; }
"""


def main(paths: list[str]) -> None:
    browser = next((b for b in BROWSERS if Path(b).exists()), None)
    if not browser:
        sys.exit("[ERROR] Chrome か Edge が見つかりません")
    for p in map(Path, paths):
        body = markdown.markdown(p.read_text(encoding="utf-8"), extensions=["tables", "fenced_code", "sane_lists"])
        html = f"<!doctype html><html lang='ja'><head><meta charset='utf-8'><title>{p.stem}</title><style>{CSS}</style></head><body>{body}</body></html>"
        with tempfile.TemporaryDirectory() as d:
            h = Path(d) / "in.html"
            h.write_text(html, encoding="utf-8")
            out = p.with_suffix(".pdf")
            subprocess.run([browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                            f"--print-to-pdf={out.resolve()}", h.resolve().as_uri()],
                           check=True, capture_output=True, timeout=120)
        print(f"[OK] {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
