#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""判定を速くするためのローカル閲覧アプリを生成する。

**このツールは判定を一切行わない。** キーボード1打で「人が下した判定」を記録するだけ。
自動で Include / Exclude を書き込む機能は意図的に持たせていない。理由:

  κ は校正セット(calibration=Y)で **著者 × 各評価者** のペアについて算出する
  (`score_screening.py` の「ペアごとの Cohen's κ」)。著者側の判定が正規表現の
  出力だと、κ は「評価者間の一致」ではなく「人 vs 正規表現の一致」を測ることになり、
  報告値が無意味になる。rule.md §プロトコル改訂(2026-07-16) が
  「意味的判断は人手ダブルスクリーニング」と定めているのもこのため。

  したがって本ツールが提供するのは **読む速度** であって **判断の代行** ではない。
  キーワードは「並べ替え」と「ハイライト」にのみ使う(下記 --rules)。

入力:  screening/sheet_<id>.csv (雛形。既に xlsx に記入があればそれも読む)
出力:  screening/review_<id>.html  … 単体で開けるHTML(依存なし・オフライン動作)

使い方:
    python -X utf8 scripts/make_review_app.py                # 著者用
    python -X utf8 scripts/make_review_app.py --id kataoka   # 評価者用
    python -X utf8 scripts/make_review_app.py --rules my_rules.json

生成した HTML をブラウザで開き、キーボードで判定する。判定は逐次 localStorage に
保存され、`E` キーで decisions CSV を書き出す。CSV を xlsx へ反映するのは
`scripts/apply_review_decisions.py`。
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
csv.field_size_limit(10 ** 9)

# 統制語彙は xlsx 生成側が正。ここで定義し直すと必ず乖離する。
from make_screening_xlsx import DECISIONS, EXCLUDE_REASONS, REASON_OTHER  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCREENING = ROOT / "screening"

# ハイライト語。
#   group1-3 は実行済み検索クエリの3概念群 (docs/protocol/search_strings.md Rev.6)。
#   cue は PICOS の判断材料になりやすい語。**両方向(残す手がかり/落とす手がかり)を
#   対称に入れてある。**片側だけ光らせると誘導になるため。
HIGHLIGHT = {
    "g1": ["virtual reality", "VR", "HMD", "head-mounted display", "head mounted display",
           "virtual environment", "immersive virtual", "immersive"],
    "g2": ["avatar", "body", "embodiment", "self-avatar", "body ownership", "virtual body"],
    "g3": ["size", "scale", "scaling", "height", "distance", "eye height", "proportion"],
    "cue": ["participants", "participant", "subjects", "user study", "we conducted",
            "experiment", "within-subjects", "between-subjects", "questionnaire",
            "desktop", "monitor", "CAVE", "augmented reality", "AR", "mixed reality",
            "patients", "children", "elderly", "clinical", "rehabilitation", "surgeon",
            "we present", "we propose", "prototype", "demonstration",
            "survey", "review", "state of the art"],
}


def load_records(sheet_id: str) -> list[dict]:
    """雛形 CSV を読み、同名 xlsx に既存の記入があれば取り込む。"""
    csv_path = SCREENING / f"sheet_{sheet_id}.csv"
    if not csv_path.exists():
        sys.exit(f"[ERROR] {csv_path} が無い。先に make_screening_sheets.py を実行すること。")
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("record_id")]

    # 校正セットの正は assignment.csv。sheet_*.csv は生成時点のスナップショットなので、
    # Rev.22(校正セット 15%→20%)のようにあとから割当が変わるとズレる。
    # ★ の表示を誤ると「κ に効く文献」を見落とすので、必ず assignment 側で上書きする。
    apath = SCREENING / "assignment.csv"
    if apath.exists():
        with apath.open(encoding="utf-8-sig", newline="") as f:
            cal = {r["record_id"]: r.get("calibration", "N")
                   for r in csv.DictReader(f) if r.get("record_id")}
        drift = 0
        for r in rows:
            want = cal.get(r["record_id"], r.get("calibration", "N"))
            if want != r.get("calibration"):
                r["calibration"] = want
                drift += 1
        if drift:
            print(f"[INFO] assignment.csv により校正セット表示を {drift} 件補正した"
                  f"（sheet_{sheet_id}.csv が割当より古い）。")

    xlsx_path = SCREENING / f"sheet_{sheet_id}.xlsx"
    if xlsx_path.exists():
        try:
            from openpyxl import load_workbook
        except ImportError:
            print("[WARN] openpyxl が無いため xlsx の既存記入は取り込まない。")
        else:
            wb = load_workbook(xlsx_path, read_only=True, data_only=True)
            ws = wb["判定"]
            it = ws.iter_rows(values_only=True)
            header = list(next(it))
            idx = {name: header.index(name) for name in ("ID", "判定 ★", "除外理由 ★", "メモ")
                   if name in header}
            existing = {}
            for row in it:
                rid = row[idx["ID"]] if idx.get("ID") is not None else None
                if not rid:
                    continue
                existing[str(rid)] = {
                    "decision": row[idx["判定 ★"]] or "",
                    "reason": row[idx["除外理由 ★"]] or "",
                    "note": row[idx["メモ"]] or "",
                }
            wb.close()
            n = 0
            for r in rows:
                got = existing.get(r["record_id"])
                if got and str(got["decision"]).strip():
                    r["decision"], r["reason"], r["note"] = (
                        str(got["decision"]).strip(), str(got["reason"] or "").strip(),
                        str(got["note"] or "").strip())
                    n += 1
            if n:
                print(f"[INFO] xlsx から既存の判定 {n} 件を取り込んだ。")
    return rows


def build_payload(rows: list[dict]) -> list[dict]:
    keep = ("record_id", "title", "abstract", "venue", "year", "rank", "has_abstract",
            "source", "calibration", "abstract_source", "kw_groups", "doi",
            "decision", "reason", "note")
    out = []
    for r in rows:
        out.append({k: (r.get(k) or "") for k in keep})
    return out


def render(sheet_id: str, records: list[dict], rules: list[dict]) -> str:
    payload = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    reasons = json.dumps([{"value": v, "desc": d} for v, d in EXCLUDE_REASONS],
                         ensure_ascii=False)
    return TEMPLATE.replace("__SHEET_ID__", html.escape(sheet_id)) \
                   .replace("__RECORDS__", payload) \
                   .replace("__REASONS__", reasons) \
                   .replace("__DECISIONS__", json.dumps(DECISIONS, ensure_ascii=False)) \
                   .replace("__REASON_OTHER__", json.dumps(REASON_OTHER, ensure_ascii=False)) \
                   .replace("__HIGHLIGHT__", json.dumps(HIGHLIGHT, ensure_ascii=False)) \
                   .replace("__RULES__", json.dumps(rules, ensure_ascii=False))


TEMPLATE = r"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Phase 3b 判定 — __SHEET_ID__</title>
<style>
:root{
  --bg:#ffffff; --fg:#1a1a1a; --muted:#6b7280; --line:#e5e7eb; --soft:#f6f8fa;
  --accent:#1f4e79; --inc:#0f7b3f; --exc:#b02a37; --uns:#b26a00;
  --g1:#dbeafe; --g2:#dcfce7; --g3:#fef3c7; --cue:#ede9fe; --cal:#fdf1e7;
}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
  --bg:#111418; --fg:#e6e8eb; --muted:#9aa4b2; --line:#2a3038; --soft:#171b21;
  --accent:#7fb0e0; --inc:#4ade80; --exc:#f87171; --uns:#fbbf24;
  --g1:#1e3a5f; --g2:#14532d; --g3:#5c4708; --cue:#3b2f6b; --cal:#4a3520;
}}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--fg);
  font-family:system-ui,"Segoe UI","Hiragino Kaku Gothic ProN","Yu Gothic UI",sans-serif;}
#bar{position:sticky;top:0;z-index:10;background:var(--bg);border-bottom:1px solid var(--line);
  padding:8px 16px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;font-size:13px}
#prog{flex:1;min-width:160px;height:8px;background:var(--soft);border-radius:99px;overflow:hidden}
#progfill{height:100%;background:var(--accent);width:0%}
.pill{padding:2px 9px;border-radius:99px;background:var(--soft);white-space:nowrap}
.pill b{font-variant-numeric:tabular-nums}
main{max-width:920px;margin:0 auto;padding:22px 20px 120px}
.meta{display:flex;gap:10px;flex-wrap:wrap;align-items:center;font-size:12.5px;color:var(--muted);margin-bottom:10px}
.tag{padding:2px 8px;border-radius:4px;background:var(--soft);white-space:nowrap}
.tag.cal{background:var(--cal);color:var(--fg);font-weight:700}
.tag.noabs{background:var(--exc);color:#fff}
h1{font-size:21px;line-height:1.5;margin:6px 0 12px;font-weight:700}
.abs{font-size:15px;line-height:1.95;white-space:pre-wrap;
  border-left:3px solid var(--line);padding:2px 0 2px 16px;max-width:74ch}
.abs.empty{color:var(--muted);font-style:italic;border-left-color:var(--exc)}
mark{padding:0 2px;border-radius:3px;background:var(--soft);color:inherit}
mark.g1{background:var(--g1)} mark.g2{background:var(--g2)}
mark.g3{background:var(--g3)} mark.cue{background:var(--cue)}
#state{margin:22px 0 8px;font-size:15px;font-weight:700}
#state .inc{color:var(--inc)} #state .exc{color:var(--exc)} #state .uns{color:var(--uns)}
#note{width:100%;max-width:74ch;font:inherit;font-size:14px;padding:8px 10px;
  border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
#keys{position:fixed;bottom:0;left:0;right:0;background:var(--bg);
  border-top:1px solid var(--line);padding:8px 16px;font-size:12px;color:var(--muted);
  display:flex;gap:8px;flex-wrap:wrap;justify-content:center}
kbd{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--soft);
  border:1px solid var(--line);border-radius:4px;padding:1px 5px;font-size:11px;color:var(--fg)}
#help{position:fixed;inset:0;background:rgba(0,0,0,.55);display:none;z-index:50;
  align-items:center;justify-content:center;padding:20px}
#help.on{display:flex}
#helpbox{background:var(--bg);border-radius:10px;padding:22px 26px;max-width:640px;
  max-height:82vh;overflow:auto;border:1px solid var(--line)}
#helpbox table{border-collapse:collapse;width:100%;font-size:13.5px}
#helpbox td{padding:4px 8px;border-bottom:1px solid var(--line);vertical-align:top}
button{font:inherit;font-size:13px;padding:5px 11px;border:1px solid var(--line);
  border-radius:6px;background:var(--soft);color:var(--fg);cursor:pointer}
select{font:inherit;font-size:13px;padding:4px 6px;border:1px solid var(--line);
  border-radius:6px;background:var(--bg);color:var(--fg)}
.warn{background:var(--cal);border-radius:8px;padding:10px 14px;font-size:13px;margin-bottom:14px}
</style></head><body>

<div id="bar">
  <span class="pill">#<b id="pos">0</b>/<b id="total">0</b></span>
  <div id="prog"><div id="progfill"></div></div>
  <span class="pill">判定済 <b id="done">0</b></span>
  <span class="pill" style="color:var(--inc)">Inc <b id="ninc">0</b></span>
  <span class="pill" style="color:var(--exc)">Exc <b id="nexc">0</b></span>
  <span class="pill" style="color:var(--uns)">Uns <b id="nuns">0</b></span>
  <select id="filter">
    <option value="all">すべて</option>
    <option value="todo">未判定のみ</option>
    <option value="cal">校正セットのみ</option>
    <option value="noabs">要旨なしのみ</option>
    <option value="flag">ルール該当のみ</option>
  </select>
  <button id="exp">CSV書き出し (E)</button>
  <button id="hlp">? ヘルプ</button>
</div>

<main>
  <div id="calwarn" class="warn" hidden>
    <b>★ 校正セット</b> — この文献は3名全員が判定し、<b>Cohen's κ の算出に使われます。</b>
    普段どおりの基準で、ただし丁寧に読んでください。
  </div>
  <div class="meta" id="meta"></div>
  <h1 id="title"></h1>
  <div class="abs" id="abs"></div>
  <div id="state">未判定</div>
  <input id="note" placeholder="メモ（任意。除外理由が「その他」のときは必須）">
</main>

<div id="keys"></div>
<div id="help"><div id="helpbox">
  <h2 style="margin-top:0">キー操作</h2>
  <table id="helptable"></table>
  <p style="font-size:13px;color:var(--muted);margin-bottom:0">
    判定は入力のたびにブラウザに保存されます（localStorage）。作業を終えたら
    <kbd>E</kbd> で CSV を書き出し、<code>scripts/apply_review_decisions.py</code> で
    xlsx に反映してください。<br><br>
    <b>このツールは判定を自動化しません。</b> キーワードルールはハイライトと並べ替えだけに
    使われ、Include / Exclude を書き込むことはありません。
  </p>
</div></div>

<script>
const RECORDS=__RECORDS__, REASONS=__REASONS__, DECISIONS=__DECISIONS__;
const REASON_OTHER=__REASON_OTHER__, HIGHLIGHT=__HIGHLIGHT__, RULES=__RULES__;
const SHEET="__SHEET_ID__", KEY="phase3b:"+SHEET;

let store={};
try{store=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){store={}}
// 生成時に xlsx から取り込んだ判定は、localStorage が空のときだけ初期値にする。
RECORDS.forEach(r=>{ if(!store[r.record_id] && r.decision)
  store[r.record_id]={decision:r.decision,reason:r.reason||"",note:r.note||""}; });

function matchRules(r){
  const hay=((r.title||"")+" "+(r.abstract||"")+" "+(r.venue||"")).toLowerCase();
  return RULES.filter(ru=>(ru.any||[]).some(w=>hay.includes(String(w).toLowerCase())))
              .map(ru=>ru.label||"rule");
}
RECORDS.forEach(r=>{ r._flags=matchRules(r); });

let order=RECORDS.map((_,i)=>i), view=[], cur=0;
function rebuild(keepId){
  const f=document.getElementById("filter").value;
  view=order.filter(i=>{const r=RECORDS[i],s=store[r.record_id];
    if(f==="todo")  return !(s&&s.decision);
    if(f==="cal")   return r.calibration==="Y";
    if(f==="noabs") return r.has_abstract==="N";
    if(f==="flag")  return r._flags.length>0;
    return true;});
  if(!view.length){view=order.slice()}
  if(keepId!==undefined){const k=view.findIndex(i=>RECORDS[i].record_id===keepId); if(k>=0)cur=k;}
  cur=Math.max(0,Math.min(cur,view.length-1));
  draw();
}

function esc(s){return (s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]))}
let hlOn=true;
function highlight(text){
  let out=esc(text);
  if(!hlOn) return out;
  for(const cls of ["g1","g2","g3","cue"]){
    const terms=[...HIGHLIGHT[cls]].sort((a,b)=>b.length-a.length);
    for(const t of terms){
      const pat=t.replace(/[.*+?^${}()|[\]\\]/g,"\\$&").replace(/[\s-]/g,"[\\s-]");
      out=out.replace(new RegExp("(?<![\\w>])("+pat+")(?![\\w])","gi"),
                      m=>'<mark class="'+cls+'">'+m+'</mark>');
    }
  }
  return out;
}

function draw(){
  const r=RECORDS[view[cur]], s=store[r.record_id]||{};
  document.getElementById("pos").textContent=cur+1;
  document.getElementById("total").textContent=view.length;
  const tags=[];
  if(r.calibration==="Y") tags.push('<span class="tag cal">★ 校正セット</span>');
  if(r.has_abstract==="N") tags.push('<span class="tag noabs">要旨なし</span>');
  tags.push('<span class="tag">'+esc(r.venue)+'</span>');
  tags.push('<span class="tag">'+esc(r.year)+'</span>');
  if(r.rank) tags.push('<span class="tag">'+esc(r.rank)+'</span>');
  tags.push('<span class="tag">概念群 '+esc(r.kw_groups)+'</span>');
  tags.push('<span class="tag">'+esc(r.source)+'</span>');
  if(r.abstract_source==="enriched") tags.push('<span class="tag">要旨=補完</span>');
  if(r.doi) tags.push('<span class="tag">'+esc(r.doi)+'</span>');
  r._flags.forEach(f=>tags.push('<span class="tag" style="background:var(--cue)">▶ '+esc(f)+'</span>'));
  document.getElementById("meta").innerHTML=tags.join("");
  document.getElementById("calwarn").hidden=(r.calibration!=="Y");
  document.getElementById("title").innerHTML=highlight(r.title);
  const a=document.getElementById("abs");
  if(r.abstract){a.className="abs";a.innerHTML=highlight(r.abstract);}
  else{a.className="abs empty";a.textContent="（要旨なし — タイトルだけで判断できなければ Unsure に）";}
  const st=document.getElementById("state");
  if(!s.decision) st.innerHTML='<span style="color:var(--muted)">未判定</span>';
  else if(s.decision==="Include") st.innerHTML='<span class="inc">✓ Include</span>';
  else if(s.decision==="Unsure")  st.innerHTML='<span class="uns">? Unsure</span>';
  else st.innerHTML='<span class="exc">✕ Exclude</span> <span style="font-weight:400">— '+esc(s.reason)+'</span>';
  document.getElementById("note").value=s.note||"";
  stats(); window.scrollTo(0,0);
}

function stats(){
  let d=0,i=0,e=0,u=0;
  for(const r of RECORDS){const s=store[r.record_id];if(!s||!s.decision)continue;
    d++; if(s.decision==="Include")i++; else if(s.decision==="Exclude")e++; else u++;}
  document.getElementById("done").textContent=d;
  document.getElementById("ninc").textContent=i;
  document.getElementById("nexc").textContent=e;
  document.getElementById("nuns").textContent=u;
  document.getElementById("progfill").style.width=(d/RECORDS.length*100).toFixed(1)+"%";
}

let undo=[];
function set(dec,reason){
  const r=RECORDS[view[cur]];
  undo.push({id:r.record_id,prev:JSON.parse(JSON.stringify(store[r.record_id]||{}))});
  if(undo.length>200)undo.shift();
  const s=store[r.record_id]||{};
  store[r.record_id]={decision:dec,reason:dec==="Exclude"?(reason||""):"",note:s.note||""};
  save(); draw();
  if(!(dec==="Exclude"&&reason===REASON_OTHER)) next();
  else document.getElementById("note").focus();
}
function save(){localStorage.setItem(KEY,JSON.stringify(store))}
function next(){if(cur<view.length-1){cur++;draw()}else{draw()}}
function prev(){if(cur>0){cur--;draw()}}

document.getElementById("note").addEventListener("input",e=>{
  const r=RECORDS[view[cur]];
  const s=store[r.record_id]||{decision:"",reason:""};
  s.note=e.target.value; store[r.record_id]=s; save();
});

function exportCSV(){
  const head=["record_id","decision","reason","note"];
  const lines=[head.join(",")];
  for(const r of RECORDS){
    const s=store[r.record_id]; if(!s||!s.decision) continue;
    lines.push([r.record_id,s.decision,s.reason||"",s.note||""]
      .map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(","));
  }
  const blob=new Blob(["\ufeff"+lines.join("\r\n")],{type:"text/csv;charset=utf-8"});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob);
  a.download="decisions_"+SHEET+".csv"; a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),2000);
}

const KEYMAP=[
  ["i","Include"],["u","Unsure"],
  ...REASONS.map((x,n)=>[String(n+1),"Exclude — "+x.value]),
  ["j / →","次へ"],["k / ←","前へ"],["m","メモ欄へ"],["z","直前を取り消し"],
  ["h","ハイライト切替"],["e","CSV書き出し"],["?","このヘルプ"],
];
document.getElementById("keys").innerHTML=
  ['<kbd>i</kbd> Include','<kbd>u</kbd> Unsure',
   '<kbd>1</kbd>–<kbd>'+REASONS.length+'</kbd> Exclude+理由',
   '<kbd>j</kbd>/<kbd>k</kbd> 移動','<kbd>m</kbd> メモ','<kbd>z</kbd> 取消',
   '<kbd>e</kbd> 書き出し','<kbd>?</kbd> ヘルプ'].join("　");
document.getElementById("helptable").innerHTML=
  KEYMAP.map(([k,v])=>"<tr><td><kbd>"+k+"</kbd></td><td>"+esc(v)+"</td></tr>").join("")
  +REASONS.map((x,n)=>"<tr><td><kbd>"+(n+1)+"</kbd></td><td><b>"+esc(x.value)+"</b><br><span style='color:var(--muted)'>"+esc(x.desc)+"</span></td></tr>").join("");

document.addEventListener("keydown",e=>{
  if(e.target.tagName==="INPUT"||e.target.tagName==="SELECT"){
    if(e.key==="Escape"||e.key==="Enter"){e.target.blur();e.preventDefault();}
    return;
  }
  if(e.ctrlKey||e.metaKey||e.altKey) return;
  const k=e.key;
  if(k==="?"){document.getElementById("help").classList.toggle("on");e.preventDefault();return}
  if(k==="Escape"){document.getElementById("help").classList.remove("on");return}
  if(k==="i"||k==="I"){set("Include");e.preventDefault();return}
  if(k==="u"||k==="U"){set("Unsure");e.preventDefault();return}
  if(/^[1-9]$/.test(k)){const n=+k-1; if(n<REASONS.length){set("Exclude",REASONS[n].value);e.preventDefault();}return}
  if(k==="j"||k==="ArrowRight"||k===" "){next();e.preventDefault();return}
  if(k==="k"||k==="ArrowLeft"){prev();e.preventDefault();return}
  if(k==="m"||k==="M"){document.getElementById("note").focus();e.preventDefault();return}
  if(k==="h"||k==="H"){hlOn=!hlOn;draw();return}
  if(k==="e"||k==="E"){exportCSV();return}
  if(k==="z"||k==="Z"){const u=undo.pop(); if(u){ if(u.prev&&u.prev.decision)store[u.id]=u.prev; else delete store[u.id];
    save(); rebuild(u.id);} return}
});
document.getElementById("exp").onclick=exportCSV;
document.getElementById("hlp").onclick=()=>document.getElementById("help").classList.toggle("on");
document.getElementById("filter").onchange=()=>{cur=0;rebuild()};
window.addEventListener("beforeunload",e=>{
  const any=Object.keys(store).length; if(any){e.preventDefault();e.returnValue=""}
});
rebuild();
</script></body></html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", default="author", help="シートID (既定: author)")
    ap.add_argument("--rules", type=Path,
                    help='キーワードルールJSON: [{"label":"臨床?","any":["patient","surgery"]}] '
                         "— ハイライトと並べ替えにのみ使う。判定は書き込まない")
    ap.add_argument("--out", type=Path, help="出力先HTML")
    args = ap.parse_args()

    rules = []
    if args.rules:
        rules = json.loads(args.rules.read_text(encoding="utf-8"))
        if not isinstance(rules, list):
            sys.exit("[ERROR] --rules は配列であること")

    rows = load_records(args.id)
    out = args.out or (SCREENING / f"review_{args.id}.html")
    out.write_text(render(args.id, build_payload(rows), rules), encoding="utf-8")

    ndone = sum(1 for r in rows if (r.get("decision") or "").strip())
    ncal = sum(1 for r in rows if r.get("calibration") == "Y")
    print(f"[OK] {out}")
    print(f"     {len(rows):,} 件（校正セット {ncal:,} 件 / 既存の判定 {ndone:,} 件）")
    print(f"     ブラウザで開いて判定 → E キーで decisions_{args.id}.csv を書き出す")
    print(f"     反映: python -X utf8 scripts/apply_review_decisions.py "
          f"--id {args.id} --input decisions_{args.id}.csv")


if __name__ == "__main__":
    main()
