"""体形(太る・痩せる等)の語を含む記録が、スクリーニングのどの段で落ちたかを追跡する。

使い方: python -X utf8 scripts/trace_body_shape.py outputs/body_shape_trace.csv
(SurveyProtocol/ をカレントにして実行。記録: docs/reference/body_shape_scope_analysis.md)
"""
import csv, re, sys
sys.path.insert(0, 'scripts'); sys.path.insert(0, '.')
from make_screening_sheets import record_key, record_id
csv.field_size_limit(10**9)
P='data/pipeline/'
def rd(f): return list(csv.DictReader(open(f, encoding='utf-8-sig')))
SHAPE = re.compile(r"\b(body[- ]?weight|weight perception|perceived weight|(over|under)weight|obes\w*|fat(ter|ness)?|thin(ner|ness)?|slim(mer|ming)?|skinn\w*|body[- ]?shape\w*|body[- ]?image|body (dis)?satisfaction|bmi|body[- ]?mass|waist\w*|belly|abdom\w*|girth|body[- ]?width|plus[- ]size|eating disorder\w*|anorexi\w*|bulimi\w*|heav(y|ier) (body|avatar)|light(er)? (body|avatar))\b", re.I)
dedup = rd(P+'step1_dedup.csv')
f15 = {r['Key']: r for r in rd(P+'step1_5_filter_excluded.csv')}
s2x = {r['Key']: r for r in rd(P+'step2_rank_excluded.csv')}
s3x = {r['Key']: r for r in rd(P+'step3_kw_excluded.csv')}
s3i = {r['Key'] for r in rd(P+'step3_kw_included.csv')}
st1 = {r['record_id']: r for r in rd('screening/stage1/sheet_author.csv')}
fin = {r['record_id']: r for r in rd('screening/final/final_decisions.csv')}
man = {r['record_id'] for r in rd('fulltext/manifest.csv')}
out=[]
for r in dedup:
    t=(r['Title'] or '')+' '+(r['Abstract Note'] or '')
    m=sorted({x.group(0).lower() for x in SHAPE.finditer(t)})
    if not m: continue
    k=r['Key']; rid=record_id(record_key(r))
    if k in f15: stage='P1.5 filter: '+f15[k].get('Filter_Layer_Reason','')
    elif k in s2x: stage='P2 venue: '+s2x[k].get('Excl_Reason_Phase2','')
    elif k in s3x: stage='P3a kw: '+s3x[k].get('KW_Excl_Category','')+' '+s3x[k].get('KW_Excl_Keywords','')
    elif k in s3i:
        a=st1.get(rid,{}); f=fin.get(rid)
        if rid in man: stage='Phase4 対象'
        elif f: stage=f"P3b final {f['final_decision']} (A:{f['reason_a']} / B:{f['reason_b']})"
        else: stage=f"P3b stage1 {a.get('decision','?')} {a.get('reason','')}"
    else: stage='?'
    out.append(dict(Key=k,rid=rid,year=r['Publication Year'],title=r['Title'],venue=r['Publication Title'],terms=';'.join(m),stage=stage))
w=csv.DictWriter(open(sys.argv[1],'w',encoding='utf-8-sig',newline=''),fieldnames=list(out[0]))
w.writeheader(); w.writerows(out)
from collections import Counter
print(len(out)); print(Counter(o['stage'].split(':')[0].split(' (')[0] for o in out).most_common())
