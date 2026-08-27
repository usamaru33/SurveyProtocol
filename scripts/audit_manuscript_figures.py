# -*- coding: utf-8 -*-
"""原稿 (SelfScaleSurvey/main.tex) の数値を実データと突合する監査スクリプト。

    python -X utf8 scripts/audit_manuscript_figures.py

SurveyProtocol/ をカレントに置いて実行する。判定シートは読み取りのみで、
step ファイル・シートには一切書き込まない(Phase 3b 凍結を侵さない)。

2026-08-23 の監査で以下の齟齬を検出し原稿を是正した。再発検知のため常設する。
  - gold set 12件時代の記述が §5.3 と Threats に残存(実データは17件)
  - Phase 3a の内訳が合計と不一致(113+24+262=399 に対し実除外は384)
  - 引用探索のチェーンが1件合わない(タイトル未解決は3行=2レコード)
  - 1.5層の「要旨欠落567件」が pipeline.py の stale なコメント由来(実測3,707)
  - known-item table のキャプションが「第1波のみ」だが実測は統合コーパス
"""
import csv
import io
import re
import sys

csv.field_size_limit(10 ** 8)

TEX = r'../SelfScaleSurvey/main.tex'

G = [
    ("G1", re.compile(r"\b(virtual realit\w*|vr|hmds?|head[- ]mounted displays?"
                      r"|virtual environment\w*|immersive virtual)\b", re.I)),
    ("G2", re.compile(r"\b(avatars?|bod(?:y|ies|ily)|embodiment|embodied)\b", re.I)),
    ("G3", re.compile(r"\b(sizes?|scal\w*|heights?|distances?)\b", re.I)),
]

fails = []


def load(p):
    return list(csv.DictReader(io.open(p, encoding='utf-8-sig')))


def check(label, got, want):
    ok = got == want
    print('  [%s] %-52s got=%-8s expected=%s'
          % ('OK ' if ok else 'FAIL', label, got, want))
    if not ok:
        fails.append(label)


def norm(s):
    return re.sub(r'[^a-z0-9]+', '', (s or '').lower())


tex = io.open(TEX, encoding='utf-8').read()


def in_tex(*frags):
    """原稿に当該表記が現れるか(数値の桁区切り {,} を吸収して照合)。"""
    flat = tex.replace('{,}', ',')
    return all(f in flat for f in frags)


print('== Phase 1-3a chain ==')
inc15 = load('step1_5_filter_included.csv')
exc15 = load('step1_5_filter_excluded.csv')
dedup = inc15 + exc15
check('deduplicated records', len(dedup), 18342)
n_pass = sum(1 for r in inc15 if not (r.get('Filter_Layer_Reason') or '').strip())
n_hold = len(inc15) - n_pass
check('filter layer pass', n_pass, 2610)
check('filter layer hold', n_hold, 3707)
check('filter layer excluded', len(exc15), 12025)
check('step2 retained', len(load('step2_rank_included.csv')), 1179)
kw_inc = load('step3_kw_included.csv')
kw_exc = load('step3_kw_excluded.csv')
check('step3 retained', len(kw_inc), 795)
check('step3 excluded', len(kw_exc), 384)

print()
print('== Phase 3a category membership (overlaps counted per category) ==')
cats = {'Cat1': 0, 'Cat2': 0, 'Cat3': 0}
multi = 0
for r in kw_exc:
    c = r['KW_Excl_Category']
    hit = [k for k in cats if k in c]
    for k in hit:
        cats[k] += 1
    if len(hit) > 1:
        multi += 1
check('Cat1 membership', cats['Cat1'], 119)
check('Cat2 membership', cats['Cat2'], 25)
check('Cat3 membership', cats['Cat3'], 263)
check('records in >1 category', multi, 23)
check('membership sum - overlap == excluded',
      sum(cats.values()) - multi, len(kw_exc))

print()
print('== abstract-less population at the filter layer ==')
noab = [r for r in dedup if not (r.get('Abstract Note') or '').strip()]
check('abstract-less records', len(noab), 3707)
surv = sum(1 for r in noab if all(rx.search(r.get('Title') or '') for _, rx in G))
check('abstract-less surviving a title-only test', surv, 0)

print()
print('== known-item test (17 in-scope) ==')
ki = load('outputs/known_item_test.csv')
check('gold set size (in-scope)', len(ki), 17)
for stage, want in [('step0', 13), ('step1', 13), ('step1_5', 11),
                    ('step2', 5), ('step3', 5)]:
    col = stage + '_survived'
    check(stage + ' survivors', sum(1 for r in ki if r[col].strip() == 'Y'), want)

by_doi, by_title = {}, {}
for r in dedup:
    d = (r.get('DOI') or '').strip().lower()
    if d:
        by_doi.setdefault(d, r)
    by_title.setdefault(norm(r.get('Title')), r)
in_corpus = [by_doi.get(k['DOI'].strip().lower()) or by_title.get(norm(k['Title']))
             for k in ki]
in_corpus = [r for r in in_corpus if r is not None]
check('known items present in dedup corpus', len(in_corpus), 13)
check('of those, abstract-less',
      sum(1 for r in in_corpus if not (r.get('Abstract Note') or '').strip()), 0)
check('of those, passing a title-only test',
      sum(1 for r in in_corpus
          if all(rx.search(r.get('Title') or '') for _, rx in G)), 4)

print()
print('== wave-wise retrieval recall ==')
w1 = w2 = 0
for k in ki:
    toks = [t.strip() for t in k['step0_source_dbs'].split(';') if t.strip()]
    if any('wave2' not in t for t in toks):
        w1 += 1
    if any('wave2' in t for t in toks):
        w2 += 1
check('recall, wave 1 alone', w1, 13)
check('recall, wave 2 alone', w2, 11)

print()
print('== citation searching chain ==')
sb = load('outputs/snowballing_log.csv')
new = [r for r in sb if r['in_db_already'] == 'N']
uniq = {}
for r in new:
    uniq.setdefault(r['found_doi'].strip().lower()
                    or 'T:' + r['found_title'].strip().lower(), r)
titled = [r for r in uniq.values() if r['found_title'].strip()]
sheet = load('screening/sheet_author.csv')
snow = [r for r in sheet if r['source'] == 'snowballing']
check('one-hop records', len(sb), 475)
check('already in database corpus', len(sb) - len(new), 158)
check('duplicates across seeds', len(new) - len(uniq), 30)
check('distinct records', len(uniq), 287)
check('unresolvable to a title', len(uniq) - len(titled), 2)
check('removed by Phase 3a keywords', len(titled) - len(snow), 28)
check('reaching human screening', len(snow), 257)

print()
print('== screening corpus ==')
check('total records', len(sheet), 1052)
check('database route', sum(1 for r in sheet if r['source'] == 'database'), 795)
check('calibration set', sum(1 for r in load('screening/assignment.csv')
                             if r['calibration'] == 'Y'), 223)
check('no abstract at screening',
      sum(1 for r in sheet if r['has_abstract'] == 'N'), 191)
check('abstracts recovered by enrichment',
      sum(1 for r in sheet if r['abstract_source'] == 'enriched'), 134)

print()
print('== SJR Q2 exclusion ==')
q2 = load('outputs/sjr_q2_excluded_venues.csv')
check('journals below Q1', len(q2), 332)
check('records lost to the Q1 rule',
      sum(int(r['record_count']) for r in q2), 826)

print()
print('== export completeness ==')
ec = {r['file']: r for r in load('outputs/export_completeness.csv')}
a1, a2 = ec['acm.csv'], ec['acm_wave2_20260803.csv']
check('ACM wave 1 abstracts present (%)',
      round(100 * int(a1['abstract_filled']) / int(a1['records']), 1), 4.3)
check('ACM wave 2 abstracts present (%)',
      round(100 * int(a2['abstract_filled']) / int(a2['records']), 1), 97.6)
check('Scopus wave 2 harvested records',
      int(ec['scopus_wave2_20260730.csv']['records']), 2542)

print()
print('== manuscript text carries the corrected figures ==')
for label, frags in [
    ('gold set reported as 17, not 12', ('17 in-scope items',)),
    ('Phase 3a totals reconciled', ('and excluded 384', '119 matched')),
    ('filter layer uses 3,707 not 567', ('3,707 of', 'not one of them satisfies')),
    ('citation chain closes', ('leaving 317', 'leaving 287 distinct')),
    ('wave-wise recall stated', ('13/17 (76.5\\%)', '11/17')),
    ('protocol revision count', ('revised twenty-one times',)),
]:
    check(label, in_tex(*frags), True)

print()
if fails:
    print('FAILED (%d): %s' % (len(fails), '; '.join(fails)))
    sys.exit(1)
print('All figures reconcile with the released data.')
