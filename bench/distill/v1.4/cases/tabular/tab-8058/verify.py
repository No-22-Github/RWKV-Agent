# DISTILL-CANARY-b90d62c3 : distillation case
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
for k in ['HX-2612', '0.45359237', '箱号,船次,毛重(磅)']:
    assert k in text
ND = 1
SUF = ''
rows = list(csv.DictReader(io.StringIO(case["files"]["堆场/过磅记录.csv"])))
v = sum(int(r["毛重(磅)"]) for r in rows if r["船次"] == "HX-2612") * 0.45359237
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
