# DISTILL-CANARY-7812bf66 : distillation case
import csv
import hashlib
import io
import json

def build(spec, text):
    rows = list(csv.DictReader(io.StringIO(text)))
    def keep(r):
        for col, op, val in spec.get("where", []):
            x = r[col]
            if op == "==" and x != val: return False
            if op == "!=" and x == val: return False
            if op == ">=" and float(x) < val: return False
            if op == "<" and float(x) >= val: return False
        return True
    rows = [r for r in rows if keep(r)]
    out = [spec["head"]]
    kind = spec["kind"]
    if kind in ("count", "sum"):
        agg = {}
        for r in rows:
            agg[r[spec["group"]]] = agg.get(r[spec["group"]], 0) + (1 if kind == "count" else int(r[spec["val"]]))
        vals = sorted(agg.values())
        assert len(set(vals)) == len(vals), "tie"
        for g, v in sorted(agg.items(), key=lambda kv: -kv[1]):
            out.append(spec["fmt"].format(g=g, v=v))
    elif kind == "filter":
        for r in rows:
            out.append(spec["fmt"].format(**r))
        if spec.get("tail"):
            out.append(spec["tail"].format(n=len(rows)))
    elif kind == "extreme":
        vs = sorted(int(r[spec["val"]]) for r in rows)
        assert vs[0] != vs[1] and vs[-1] != vs[-2], "tie"
        hi = [r for r in rows if int(r[spec["val"]]) == vs[-1]][0]
        lo = [r for r in rows if int(r[spec["val"]]) == vs[0]][0]
        out.append(spec["fmt_hi"].format(**hi))
        out.append(spec["fmt_lo"].format(**lo))
    return "\n".join(out) + "\n"

case = json.load(open("case.json"))
SPEC = json.loads('{"kind": "sum", "group": "鱼种", "val": "公斤", "head": "# 9 月卸货量", "fmt": "- {g}: {v} 公斤", "file": "渔港/卸货单.csv"}')
text = case["files"][SPEC["file"]]
assert hashlib.sha256(text.encode()).hexdigest().startswith('440f0aeaa13de08b')
assert text.splitlines()[0].count(",") >= 3
print(json.dumps({"files": {'报告/卸货量.md': build(SPEC, text)}}, ensure_ascii=False))
