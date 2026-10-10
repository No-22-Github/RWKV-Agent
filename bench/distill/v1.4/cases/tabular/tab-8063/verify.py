# DISTILL-CANARY-c31a1f9f : distillation case
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
for k in ['zone ZB', '1 m3 = 1000 L', 'zone,date,minutes,l_per_min']:
    assert k in text
ND = 2
SUF = ''
rows = list(csv.DictReader(io.StringIO(case["files"]["irrigation/log.csv"])))
v = sum(int(r["minutes"]) * float(r["l_per_min"]) for r in rows if r["zone"] == "ZB") / 1000
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
