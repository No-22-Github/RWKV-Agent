# DISTILL-CANARY-fddc82fe : distillation case
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
for k in ['水产类', '元/公斤', '日期,类别,品名,数量(kg),单价(元/kg)']:
    assert k in text
ND = 2
SUF = ''
rows = list(csv.DictReader(io.StringIO(case["files"]["采购/9月进货.csv"])))
v = sum(float(r["数量(kg)"]) * float(r["单价(元/kg)"]) for r in rows if r["类别"] == "水产")
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
