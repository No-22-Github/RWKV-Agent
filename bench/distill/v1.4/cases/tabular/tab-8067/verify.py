# DISTILL-CANARY-4fbcf816 : distillation case
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
for k in ['NGB-HAM', '24 hours per day', 'shipment,lane,transit_hours']:
    assert k in text
ND = 2
SUF = ''
rows = list(csv.DictReader(io.StringIO(case["files"]["freight/transit.csv"])))
s = [int(r["transit_hours"]) for r in rows if r["lane"] == "NGB-HAM"]
v = sum(s) / len(s) / 24
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
