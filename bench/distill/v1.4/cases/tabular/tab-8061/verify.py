# DISTILL-CANARY-82bc8494 : distillation case
import csv
import io
import json
import re

def fmt(v, nd):
    if nd == 0:
        return sorted({"%d" % v, "{:,}".format(int(v))})
    s = {"%.*f" % (nd, v), "{:,.{}f}".format(v, nd)}
    s |= {x.rstrip("0").rstrip(".") for x in list(s)}
    return sorted(s)

case = json.load(open("case.json"))
text = case["turns"][0]["prompt"] + "".join(case["files"].values())
for k in ['LOT-C', 'qc/lot-results.csv', 'lot,inspected,rejected']:
    assert k in text
ND = 2
SUF = '%'
rows = list(csv.DictReader(io.StringIO(case["files"]["qc/lot-results.csv"])))
s = [r for r in rows if r["lot"].startswith("LOT-C")]
v = sum(int(r["rejected"]) for r in s) / sum(int(r["inspected"]) for r in s) * 100
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
