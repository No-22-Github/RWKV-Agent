# DISTILL-CANARY-4dbcc572 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
east = list(csv.DictReader(io.StringIO(case["files"]["stock/shelf-east.csv"])))
west = list(csv.DictReader(io.StringIO(case["files"]["stock/shelf-west.csv"])))
def titles(rows):
    out = []
    for r in rows:
        t = (r.get("茶品") or "").strip()
        if t:
            out.append(t)
    return out
et, wt = titles(east), titles(west)
union = sorted(set(et) | set(wt))
overlap = sorted(set(et) & set(wt))
if not union:
    raise SystemExit(1)
facts = [
    "%d 种茶" % len(union),
]
facts.extend(overlap)
print(json.dumps({"expected_contains_any": facts}))
