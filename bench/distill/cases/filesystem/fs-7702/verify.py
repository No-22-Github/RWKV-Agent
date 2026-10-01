# DISTILL-CANARY-4a440503 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
north = list(csv.DictReader(io.StringIO(case["files"]["stock/manifest-north.csv"])))
south = list(csv.DictReader(io.StringIO(case["files"]["stock/manifest-south.csv"])))
def titles(rows):
    out = []
    for r in rows:
        t = (r.get("title") or "").strip()
        if t:
            out.append(t)
    return out
nt, st = titles(north), titles(south)
union = sorted(set(nt) | set(st))
overlap = sorted(set(nt) & set(st))
if not union:
    raise SystemExit(1)
facts = [
    "%d titles" % len(union),
]
facts.extend(overlap)
print(json.dumps({"expected_contains_any": facts}))
