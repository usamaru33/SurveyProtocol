"""run_locate.py の出力を検査する(決定論的)。

1. 応答が JSON で、17 個のキーがあるか。
2. 各引用が、全文テキスト(fulltext/txt)に文字列として存在するか。
   照合の前に、両方を正規化する: Unicode の NFKC(PDF の合字 ﬁ・ﬃ を fi・ffi にそろえる)、ソフトハイフン U+00AD の削除、
   曲がった引用符を直線に、大文字を小文字に。
   exact = 空白の連続を 1 個にそろえて一致 / loose = 空白をすべて除いて一致(行末の改行・ハイフン分割の差を無視)。
   page_ok = 示された頁の中にあるか。
3. 複数の run があれば、列ごとに引用の集合が一致するか。

使い方: python -X utf8 verify_locate.py <model> <run 番号...>
出力: runs/<model>/verify_run<k>.csv、runs/<model>/stability.csv(run が 2 つ以上のとき)
"""
import csv, json, re, sys, pathlib, collections, unicodedata

HERE = pathlib.Path(__file__).resolve().parent
TXT = HERE.parents[2] / 'fulltext' / 'txt'
FIELDS = ['n_total', 'n_analyzed', 'population', 'device', 'scale_target', 'scale_factor', 'scale_direction',
          'non_visual', 'non_visual_detail', 'action_contingent', 'task', 'outcome_measures', 'social_context',
          'individual_diff', 'null_effect', 'main_finding', 'attribution_quote']


def canon(s):
    s = unicodedata.normalize('NFKC', s).replace('­', '')
    return s.translate(str.maketrans({'’': "'", '‘': "'", '“': '"', '”': '"'})).lower()


def ws1(s):
    return re.sub(r'\s+', ' ', canon(s)).strip()


def ws0(s):
    return re.sub(r'\s+', '', canon(s))


def pages(rid):
    t = (TXT / f'{rid}.txt').read_text(encoding='utf-8')
    parts = re.split(r'^\[p\.(\d+)\]\s*$', t, flags=re.M)
    return {int(parts[i]): parts[i + 1] for i in range(1, len(parts) - 1, 2)}, t


def parse(rec):
    r = rec['response'].get('result', '') if isinstance(rec['response'], dict) else ''
    r = r.strip()
    m = re.search(r'\{.*\}', r, flags=re.S)
    return json.loads(m.group(0)) if m else None


def load(model, k):
    out = {}
    for f in sorted((HERE / 'runs' / model / f'run{k}').glob('R*.json')):
        rec = json.loads(f.read_text(encoding='utf-8'))
        try:
            out[rec['record_id']] = parse(rec)
        except Exception:
            out[rec['record_id']] = None
    return out


def main():
    model, runs = sys.argv[1], sys.argv[2:]
    data = {k: load(model, k) for k in runs}
    for k in runs:
        rows, tot = [], collections.Counter()
        for rid, d in data[k].items():
            if not d or 'fields' not in d:
                rows.append([rid, '', '', '', 'PARSE_ERROR', '', '', ''])
                tot['parse_error'] += 1
                continue
            pg, full = pages(rid)
            miss = [f for f in FIELDS if f not in d['fields']]
            if miss:
                tot['missing_keys'] += 1
            for f in FIELDS:
                qs = d['fields'].get(f, [])
                if not qs:
                    rows.append([rid, f, '', '', 'EMPTY', '', '', ''])
                    tot['empty_fields'] += 1
                for q in qs:
                    quote, page = q.get('quote', ''), q.get('page')
                    ptxt = pg.get(page, '') if isinstance(page, int) else ''
                    exact = ws1(quote) in ws1(full)
                    loose = ws0(quote) in ws0(full)
                    page_ok = ws0(quote) in ws0(ptxt)
                    st = 'OK' if exact and page_ok else 'OK_LOOSE' if loose and page_ok else \
                        'WRONG_PAGE' if loose else 'NOT_FOUND'
                    tot[st] += 1
                    rows.append([rid, f, page, len(quote), st, int(exact), int(loose), quote])
        with open(HERE / 'runs' / model / f'verify_run{k}.csv', 'w', encoding='utf-8-sig', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(['record_id', 'field', 'page', 'chars', 'status', 'exact', 'loose', 'quote'])
            w.writerows(rows)
        print(f'run{k}: papers={len(data[k])}', dict(tot))
    if len(runs) > 1:
        rows, agree = [], collections.Counter()
        ids = sorted(set.intersection(*[set(data[k]) for k in runs]))
        for rid in ids:
            for f in FIELDS:
                sets = []
                for k in runs:
                    d = data[k][rid]
                    sets.append(frozenset(ws0(q.get('quote', '')) for q in (d or {}).get('fields', {}).get(f, [])))
                same = len(set(sets)) == 1
                inter, union = frozenset.intersection(*sets), frozenset.union(*sets)
                agree[f, same] += 1
                rows.append([rid, f, int(same), ' / '.join(str(len(s)) for s in sets), len(inter), len(union)])
        with open(HERE / 'runs' / model / 'stability.csv', 'w', encoding='utf-8-sig', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(['record_id', 'field', 'identical', 'n_quotes_per_run', 'n_common', 'n_union'])
            w.writerows(rows)
        print('identical across runs (field: n_identical / n_papers)')
        for f in FIELDS:
            print(f'  {f}: {agree[f, True]} / {len(ids)}')
        print('  all:', sum(v for (f, s), v in agree.items() if s), '/', len(ids) * len(FIELDS))


if __name__ == '__main__':
    main()
