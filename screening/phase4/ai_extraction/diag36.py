"""要確認の引用(PARTLY / ABSENT)を、本文の最も近い箇所と並べて表示する(原因分けの下調べ)。"""
import sys, re, unicodedata, difflib, io, contextlib
sys.argv = ['x', 'NUL']
with contextlib.redirect_stdout(io.StringIO()):
    import build_result_xlsx as B
bad = [x for x in B.quotes if x[5] in ('PARTLY', 'ABSENT')]
out = []
for n, (rid, f, k, pg, q, st, iv) in enumerate(bad, 1):
    raw = (B.TXT / f'{rid}.txt').read_text(encoding='utf-8')
    full = B.nh(raw)
    qq = B.nh(q)
    sm = difflib.SequenceMatcher(None, full, qq, autojunk=False)
    # 引用を 30 字ごとに分け、各片が本文のどこにあるか
    pieces = [qq[i:i + 30] for i in range(0, len(qq), 30)]
    pos = [full.find(p) for p in pieces]
    m = sm.find_longest_match(0, len(full), 0, len(qq))
    ctx_s = max(0, m.a - 60); ctx_e = min(len(full), m.a + m.size + 200)
    out.append(f'#{n} {rid} {f} run{k} p.{pg} {st} len={len(qq)} pieces_found={sum(p>=0 for p in pos)}/{len(pos)} longest={m.size}\n'
               f'  Q: {q[:260]!r}\n  T: {full[ctx_s:ctx_e]!r}\n  pos={pos}')
print('\n'.join(out))
