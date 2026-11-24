"""v0.2(日本語)と v0.3(英語)の抜き出しテストを、build_result_xlsx.py と同じ集計で比べる(決定論的)。

使い方: python -X utf8 compare_v02_v03.py claude-sonnet-5-5 claude-sonnet-5-5_v0.3
出力: 画面に要約、runs/compare_v02_v03.json に詳細(追跡しない)
"""
import sys, json, collections, pathlib
AE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AE))
SRC = (AE / "build_result_xlsx.py").read_text(encoding="utf-8")
CORE = SRC[:SRC.index("BLUE = PatternFill")]


def stats(model_dir):
    g = {"__name__": "x"}
    exec(CORE.replace("MODEL = 'claude-sonnet-5-5'", f"MODEL = {model_dir!r}"), g)
    quotes, cell, meta, ids, FIELDS = g["quotes"], g["cell"], g["meta"], g["ids"], g["FIELDS"]
    stc = collections.Counter(x[5] for x in quotes)
    nz = [c for c in cell.values() if not c["empty_all"]]
    per_field = {}
    for f in FIELDS:
        cs = [cell[r, f] for r in ids]
        nzf = [c for c in cs if not c["empty_all"]]
        per_field[f] = dict(n_quotes=sum(1 for x in quotes if x[1] == f),
                            empty_all=sum(c["empty_all"] for c in cs),
                            shared_nz=f"{sum(c['shared'] for c in nzf)}/{len(nzf)}",
                            same=sum(c["same_text"] for c in cs))
    parse_err = sum(1 for k, v in g["data"].items() if not v or "fields" not in v)
    return dict(
        papers=len(ids), runs=len({k for k, _ in g["data"]}), parse_error=parse_err,
        quotes=len(quotes), per_paper_run=round(len(quotes) / (len(ids) * 3), 1),
        OK=stc["OK"], WRONG_PAGE=stc["WRONG_PAGE"], PARTLY=stc["PARTLY"], ABSENT=stc["ABSENT"],
        match_rate=round((stc["OK"] + stc["WRONG_PAGE"]) / len(quotes) * 100, 2),
        cells=len(cell), empty_all=sum(c["empty_all"] for c in cell.values()),
        same_text=sum(c["same_text"] for c in cell.values()),
        shared_nz=f"{sum(c['shared'] for c in nz)}/{len(nz)}",
        jaccard=round(sum(c["jac"] for c in nz) / len(nz), 3),
        cost=round(sum((m["response"].get("total_cost_usd") or 0) for m in meta.values()), 2),
        minutes=round(sum((m["response"].get("duration_ms") or 0) for m in meta.values()) / 60000, 1),
        empty_cells=sorted((r, f) for (r, f), c in cell.items() if c["empty_all"]),
        bad=[(x[0], x[1], x[2], x[3], x[5], x[4]) for x in quotes if x[5] in ("PARTLY", "ABSENT")],
        per_field=per_field,
    )


if __name__ == "__main__":
    out = {m: stats(m) for m in sys.argv[1:]}
    json.dump(out, open(AE / "runs" / "compare_v02_v03.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for m, s in out.items():
        print("==", m)
        for k, v in s.items():
            if k not in ("bad", "per_field", "empty_cells"):
                print(f"  {k}: {v}")
        print("  empty_cells:", len(s["empty_cells"]), "bad:", len(s["bad"]))
