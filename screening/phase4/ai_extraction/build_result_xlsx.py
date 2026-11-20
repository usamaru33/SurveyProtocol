"""AI 抜き出しテストの結果を Excel にまとめる(決定論的。AI は使わない)。

照合は verify_locate.py と同じ規則(NFKC 正規化・空白を無視)に、行末ハイフンの違いを無視する規則を足した。
一致の測り方は 2 通り:
  - 文字列の完全一致(引用の集合が同じか)
  - 本文上の範囲の重なり(同じ箇所を指しているか。切り方の違いは無視する)

使い方: python -X utf8 build_result_xlsx.py <出力.xlsx>
"""
import csv, json, re, sys, pathlib, collections, unicodedata, itertools
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from verify_locate import FIELDS, parse, TXT, HERE, canon

MODEL = 'claude-sonnet-5-5'
RUNS = ['1', '2', '3']
ASSIGN = HERE.parent / 'assignment.csv'


def n0(s):
    return re.sub(r'\s+', '', canon(s))


def nh(s):
    return n0(s).replace('-', '')


def page_texts(rid):
    t = (TXT / f'{rid}.txt').read_text(encoding='utf-8')
    parts = re.split(r'^\[p\.(\d+)\]\s*$', t, flags=re.M)
    pg = {int(parts[i]): nh(parts[i + 1]) for i in range(1, len(parts) - 1, 2)}
    off, acc = {}, 0
    for p in sorted(pg):
        off[p] = acc
        acc += len(pg[p])
    return pg, off


def locate(rid, quote, page, cache):
    if rid not in cache:
        cache[rid] = page_texts(rid)
    pg, off = cache[rid]
    q = nh(quote)
    if not q:
        return 'ABSENT', None
    if isinstance(page, int) and page in pg:
        i = pg[page].find(q)
        if i >= 0:
            return 'OK', (off[page] + i, off[page] + i + len(q))
    for p in sorted(pg):
        i = pg[p].find(q)
        if i >= 0:
            return 'WRONG_PAGE', (off[p] + i, off[p] + i + len(q))
    joined = ''.join(pg[p] for p in sorted(pg))
    i = joined.find(q)
    if i >= 0:
        return 'WRONG_PAGE', (i, i + len(q))
    pieces = [q[k:k + 40] for k in range(0, max(len(q) - 39, 1), 40)]
    hit = sum(x in joined for x in pieces) / len(pieces)
    return ('PARTLY' if hit >= 0.3 else 'ABSENT'), None


def cover(intervals):
    s = set()
    for a, b in intervals:
        s.update(range(a, b))
    return s


ass = {r['record_id']: r for r in csv.DictReader(open(ASSIGN, encoding='utf-8-sig'))}
meta, data = {}, {}
for k in RUNS:
    for f in sorted((HERE / 'runs' / MODEL / f'run{k}').glob('R*.json')):
        rec = json.loads(f.read_text(encoding='utf-8'))
        data[k, rec['record_id']] = parse(rec)
        meta[k, rec['record_id']] = rec
ids = sorted({i for _, i in data})

cache = {}
quotes = []
for (k, rid), d in sorted(data.items(), key=lambda x: (x[0][1], x[0][0])):
    for fld in FIELDS:
        for q in (d or {}).get('fields', {}).get(fld, []):
            st, iv = locate(rid, q.get('quote', ''), q.get('page'), cache)
            quotes.append((rid, fld, k, q.get('page'), q.get('quote', ''), st, iv))

by = collections.defaultdict(list)
for x in quotes:
    by[x[0], x[1], x[2]].append(x)
cell = {}
for rid in ids:
    for fld in FIELDS:
        per = [by[rid, fld, k] for k in RUNS]
        sets = [frozenset(n0(x[4]) for x in p) for p in per]
        covs = [cover([x[6] for x in p if x[6]]) for p in per]
        pj = []
        for a, b in itertools.combinations(range(3), 2):
            u = covs[a] | covs[b]
            pj.append(1.0 if not u else len(covs[a] & covs[b]) / len(u))
        cell[rid, fld] = dict(n=[len(p) for p in per], same_text=len(set(sets)) == 1, jac=sum(pj) / 3,
                              found=sum(1 for c in covs if c), shared=bool(covs[0] & covs[1] & covs[2]),
                              empty_all=all(not c for c in covs))

BLUE = PatternFill('solid', fgColor='1F6FE0')
thin = Side(style='thin', color='BFBFBF')
B = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap = Alignment(wrap_text=True, vertical='top')
RED, YEL, GRN = (PatternFill('solid', fgColor=c) for c in ('FBE3E3', 'FFF7D6', 'DCEFE0'))
SJ = {'OK': '本文と一致', 'WRONG_PAGE': '一致(頁が違う)', 'PARTLY': '一部だけ一致', 'ABSENT': '本文に無い'}
FJ = {'n_total': '全参加者数', 'n_analyzed': '分析人数', 'population': '属性・年齢・性別', 'device': 'HMD の機種',
      'scale_target': '何を変えたか', 'scale_factor': '倍率・値', 'scale_direction': '拡大か縮小か',
      'non_visual': '視覚以外の感覚', 'non_visual_detail': '提示の中身', 'action_contingent': '動作に連動',
      'task': '課題', 'outcome_measures': '測定項目', 'social_context': '他のアバター', 'individual_diff': '個人差',
      'null_effect': '効果なしの条件', 'main_finding': '主な結果', 'attribution_quote': '帰属の原文'}


def head(ws, labels):
    for j, t in enumerate(labels, 1):
        c = ws.cell(1, j, t)
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = BLUE
        c.border = B
        c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
    ws.row_dimensions[1].height = 32


def widths(ws, w_):
    for j, w in enumerate(w_, 1):
        ws.column_dimensions[L(j)].width = w


def fill_rows(ws, rows, fills=None, wrapcols=()):
    for i, row in enumerate(rows, 2):
        for j, v in enumerate(row, 1):
            c = ws.cell(i, j, v)
            c.border = B
            if j in wrapcols:
                c.alignment = wrap
            if fills and j in fills:
                f = fills[j](v, row)
                if f:
                    c.fill = f


wb = Workbook()
ws = wb.active
ws.title = '概要'
stc = collections.Counter(x[5] for x in quotes)
n_cells = len(ids) * len(FIELDS)
same_text = sum(c['same_text'] for c in cell.values())
shared = sum(c['shared'] for c in cell.values())
empty_all = sum(c['empty_all'] for c in cell.values())
nz = [c for c in cell.values() if not c['empty_all']]
mean_j = sum(c['jac'] for c in nz) / len(nz)
shared_nz = sum(c['shared'] for c in nz)
cost = sum((m['response'].get('total_cost_usd') or 0) for m in meta.values())
lines = [
    ('Phase 4 該当箇所の抜き出し — テスト結果(33 件 × 3 回)', True),
    ('作成: 2026-11-13。入力は両者 Include の 33 件の全文テキスト(`fulltext/txt/`)。プロンプトは `prompt_v0.2.txt`、モデルは claude-sonnet-5-5。', False),
    ('このテストの出力は抽出の記録には使わない(`rule.md` の Rev.31 案が未承認のため)。', False),
    ('', False),
    ('集計', True),
    (f'引用の総数(3 回の合計): {len(quotes)} 個(1 論文・1 回あたり {len(quotes) / (len(ids) * 3):.1f} 個)', False),
    (f'  本文と一致: {stc["OK"]} 個 / 一致(頁が違う): {stc["WRONG_PAGE"]} 個 / 一部だけ一致: {stc["PARTLY"]} 個 / 本文に無い: {stc["ABSENT"]} 個', False),
    ('  照合は、空白の違い・PDF の合字・行末ハイフンの違いを無視している。', False),
    (f'論文 × 列 = {n_cells} 組のうち', False),
    (f'  3 回とも引用が 0 件: {empty_all} 組(本当に記載が無いのか、見落としかは、人が本文を読まないと分からない)', False),
    (f'  3 回で引用の集合が文字列として完全に同じ: {same_text} 組({same_text / n_cells:.0%})', False),
    (f'  3 回すべてに共通する箇所がある(範囲が重なる): {shared} 組({shared / n_cells:.0%})。0 件の組を除くと {shared_nz} / {len(nz)} 組({shared_nz / len(nz):.0%})', False),
    (f'  引用がある組での、3 回の指す箇所の重なり(文字単位の Jaccard、平均): {mean_j:.2f}', False),
    (f'実行の費用の目安: {cost:.1f} ドル(99 回)', False),
    ('', False),
    ('シート', True),
    ('列別の集計: 17 列それぞれの一致の度合い。', False),
    ('論文×列: 33 件 × 17 列の 561 行。3 回の引用数、完全一致、重なり、0 件かどうか。', False),
    ('引用一覧: 出力された引用すべて(論文・列・回・頁・原文・照合結果)。', False),
    ('要確認の引用: 照合規則を直す前に本文と一致しなかった 36 個。原因を 6 種類に分けた(Claude が本文と見比べた)。右端に人が確認結果を書く欄がある。', False),
    ('3回とも0件: 3 回とも引用が出なかった組。担当者が本文を確かめて `記載なし` かどうか決める。', False),
    ('', False),
    ('読み方', True),
    ('・「完全一致」は引用の切り方が 1 文字でも違えば「違う」になる。「重なり」は、同じ箇所を指していれば切り方が違っても一致とみなす。', False),
    ('・照合に通ることは、引用が本文にあることだけを意味する。その箇所が、その列の答えとして適切かは、人が読んで判断する。', False),
]
for i, (t, b) in enumerate(lines, 1):
    ws.cell(i, 1, t).font = Font(bold=b, size=14 if i == 1 else 11)
ws.column_dimensions['A'].width = 140

ws = wb.create_sheet('列別の集計')
head(ws, ['列', '内容', '論文数', '3回とも0件', '引用の集合が完全に同じ', '3回に共通する箇所あり',
          '共通する箇所あり(0件を除く)の割合', '重なり(Jaccard 平均、0件を除く)', '引用の総数', '本文と一致しなかった引用'])
rows = []
for f in FIELDS:
    cs = [cell[r, f] for r in ids]
    nzf = [c for c in cs if not c['empty_all']]
    qs = [x for x in quotes if x[1] == f]
    rows.append([f, FJ[f], len(cs), sum(c['empty_all'] for c in cs), sum(c['same_text'] for c in cs),
                 sum(c['shared'] for c in cs),
                 round(sum(c['shared'] for c in nzf) / len(nzf), 2) if nzf else '',
                 round(sum(c['jac'] for c in nzf) / len(nzf), 2) if nzf else '',
                 len(qs), sum(1 for x in qs if x[5] in ('PARTLY', 'ABSENT'))])
fill_rows(ws, rows)
widths(ws, [20, 18, 8, 12, 16, 16, 18, 18, 10, 14])
ws.freeze_panes = 'C2'

ws = wb.create_sheet('論文×列')
head(ws, ['record_id', '抽出担当', '列', '内容', '1回目の引用数', '2回目', '3回目', '集合が完全に同じ', '3回に共通する箇所', '重なり(Jaccard)', '状況'])
rows = []
for rid in ids:
    for f in FIELDS:
        c = cell[rid, f]
        st = '3回とも0件' if c['empty_all'] else ('一部の回で0件' if c['found'] < 3 else ('共通する箇所あり' if c['shared'] else '共通する箇所なし'))
        rows.append([rid, ass.get(rid, {}).get('extractor', ''), f, FJ[f], *c['n'], '○' if c['same_text'] else '',
                     '○' if c['shared'] else '', round(c['jac'], 2), st])
fill_rows(ws, rows, {11: lambda v, r: {'3回とも0件': YEL, '一部の回で0件': YEL, '共通する箇所なし': RED}.get(v, GRN)})
widths(ws, [13, 11, 20, 18, 10, 8, 8, 12, 12, 12, 16])
ws.freeze_panes = 'D2'
ws.auto_filter.ref = f'A1:K{len(rows) + 1}'

ws = wb.create_sheet('引用一覧')
head(ws, ['record_id', '列', '内容', '回', '頁', '照合', '引用(AI の出力そのまま)'])
rows = [[rid, f, FJ[f], int(k), pgn, SJ[st], q] for rid, f, k, pgn, q, st, iv in quotes]
fill_rows(ws, rows, {6: lambda v, r: None if v == SJ['OK'] else (YEL if v == SJ['WRONG_PAGE'] else RED)}, wrapcols=(7,))
widths(ws, [13, 20, 18, 5, 6, 16, 110])
ws.freeze_panes = 'A2'
ws.auto_filter.ref = f'A1:G{len(rows) + 1}'

ws = wb.create_sheet('要確認の引用')
head(ws, ['record_id', '列', '回', '頁', '原因(Claude が本文と見比べて分類)', '原因の説明', '照合規則の修正後', '引用(AI の出力そのまま)', '確認結果(人)', 'メモ'])
labels = {(r['record_id'], r['field'], r['run']): r
          for r in csv.DictReader(open(HERE / 'runs' / MODEL / 'cause_labels.csv', encoding='utf-8-sig'))}
now = {(x[0], x[1], x[2]): x for x in quotes if x[5] in ('PARTLY', 'ABSENT')}
rows = []
for (rid, f, k), lab in sorted(labels.items(), key=lambda kv: (kv[1]['cause'], kv[0])):
    qs = [x for x in quotes if x[0] == rid and x[1] == f and x[2] == k and x[4] and (x[5] in ('PARTLY', 'ABSENT') or True)]
    # 規則修正前に要確認だった引用を、ラベルの説明文から特定できないので、修正後も要確認のものと、修正前に要確認だったものを併記する
    rows.append((rid, f, k, lab, qs))
out = []
for rid, f, k, lab, qs in rows:
    cand = [x for x in qs if x[5] in ('PARTLY', 'ABSENT')] or [x for x in qs if x[5] != 'OK']
    still = bool(now.get((rid, f, k)))
    quote_txt = (now[(rid, f, k)][4] if still else '')
    out.append([rid, f, int(k), '', lab['cause'], lab['detail'], '要確認のまま' if still else '一致(規則の修正で解消)', quote_txt, '', ''])
fill_rows(ws, out, {9: lambda v, r: YEL, 10: lambda v, r: YEL,
                    7: lambda v, r: RED if v == '要確認のまま' else GRN}, wrapcols=(6, 8))
widths(ws, [13, 20, 5, 6, 28, 60, 18, 90, 16, 30])
ws.freeze_panes = 'A2'
ws.auto_filter.ref = f'A1:J{len(out) + 1}'

ws = wb.create_sheet('3回とも0件')
head(ws, ['record_id', '抽出担当', '列', '内容', '本文を確かめた結果(人)', 'メモ'])
rows = [[rid, ass.get(rid, {}).get('extractor', ''), f, FJ[f], '', ''] for rid in ids for f in FIELDS if cell[rid, f]['empty_all']]
fill_rows(ws, rows, {5: lambda v, r: YEL, 6: lambda v, r: YEL})
widths(ws, [13, 11, 20, 18, 24, 30])
ws.freeze_panes = 'A2'

wb.save(sys.argv[1])
print(dict(stc), 'cells', n_cells, 'same_text', same_text, 'shared', shared, 'shared_nz', shared_nz, '/', len(nz),
      'empty_all', empty_all, 'jac', round(mean_j, 3), 'bad', sum(1 for x in quotes if x[5] in ('PARTLY','ABSENT')))
