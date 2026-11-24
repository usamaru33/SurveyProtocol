"""Phase 4 該当箇所の抜き出し(テスト用)。

`fulltext/txt/<record_id>.txt` を 1 件ずつ LLM に渡し、17 列の該当箇所(原文の引用と頁)を
JSON で受け取って保存する。値の読み取り・判定・分類はさせない。

プロンプト: 既定は英語版 prompt_v0.3.txt(2026-11-24。v0.2 の英訳で、指示の中身は同じ)。
11-13 のテスト(33 件 × 3 回)は日本語版 prompt_v0.2.txt で行った。再現するときは --prompt v0.2。

使い方:
    python -X utf8 run_locate.py <ids.txt> <run 番号> [--workers N] [--prompt v0.2|v0.3]

出力: runs/<model>/run<k>/<record_id>.json(v0.2)、runs/<model>_v0.3/run<k>/(v0.3)。
CLI の応答そのまま。プロンプトのファイル名・システムプロンプト・モデル ID・実行日時を含む。
照合は verify_locate.py に <model>_v0.3 を渡す。
"""
import json, subprocess, sys, tempfile, datetime, pathlib, concurrent.futures as cf

HERE = pathlib.Path(__file__).resolve().parent
TXT = HERE.parents[2] / 'fulltext' / 'txt'
MODEL = 'claude-sonnet-5-5'
# 版 → (プロンプトのファイル, システムプロンプト, runs/ の下のフォルダ名)
PROMPTS = {
    'v0.2': ('prompt_v0.2.txt', 'あなたは、系統的レビューの文献から指定された箇所を原文のまま抜き出す作業を行います。', MODEL),
    'v0.3': ('prompt_v0.3.txt', 'You extract specified passages, verbatim, from papers in a systematic review.', f'{MODEL}_v0.3'),
}
DEFAULT_PROMPT = 'v0.3'


def run_one(rid, outdir, cwd, prompt_file, system):
    out = outdir / f'{rid}.json'
    if out.exists():
        return rid, 'skip'
    text = (TXT / f'{rid}.txt').read_text(encoding='utf-8')
    prompt = (HERE / prompt_file).read_text(encoding='utf-8')
    prompt = prompt.replace('{record_id}', rid).replace('{full_text}', text)
    cmd = ['claude', '-p', '--model', MODEL, '--system-prompt', system, '--tools', '',
           '--strict-mcp-config', '--setting-sources', '', '--no-session-persistence',
           '--disable-slash-commands', '--output-format', 'json']
    started = datetime.datetime.now().isoformat(timespec='seconds')
    p = subprocess.run(cmd, input=prompt.encode('utf-8'), capture_output=True, cwd=cwd, timeout=1500)
    stdout = p.stdout.decode('utf-8', errors='replace')
    try:
        resp = json.loads(stdout)
    except Exception:
        resp = {'raw_stdout': stdout}
    rec = {'record_id': rid, 'prompt_file': prompt_file, 'system_prompt': system, 'model_requested': MODEL, 'started': started,
           'returncode': p.returncode, 'stderr': p.stderr.decode('utf-8', errors='replace')[-2000:],
           'response': resp}
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding='utf-8')
    return rid, 'ok' if p.returncode == 0 else f'rc={p.returncode}'


def main():
    ids = [x.strip() for x in open(sys.argv[1], encoding='utf-8') if x.strip()]
    k = sys.argv[2]
    workers = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 3
    ver = sys.argv[sys.argv.index('--prompt') + 1] if '--prompt' in sys.argv else DEFAULT_PROMPT
    prompt_file, system, sub = PROMPTS[ver]
    outdir = HERE / 'runs' / sub / f'run{k}'
    outdir.mkdir(parents=True, exist_ok=True)
    cwd = tempfile.mkdtemp(prefix='p4locate_')   # 空のフォルダで実行し、CLAUDE.md などを読ませない
    with cf.ThreadPoolExecutor(workers) as ex:
        for rid, st in ex.map(lambda r: run_one(r, outdir, cwd, prompt_file, system), ids):
            print(rid, st, flush=True)


if __name__ == '__main__':
    main()
