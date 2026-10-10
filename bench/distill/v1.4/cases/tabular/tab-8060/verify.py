# DISTILL-CANARY-7026330b : distillation case
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
for k in ['知行图书', '退货总册数除以发货总册数', '书名,经销商,发货册数,退货册数']:
    assert k in text
ND = 1
SUF = '%'
rows = list(csv.DictReader(io.StringIO(case["files"]["发行/退货统计.csv"])))
s = [r for r in rows if r["经销商"] == "知行图书"]
v = sum(int(r["退货册数"]) for r in s) / sum(int(r["发货册数"]) for r in s) * 100
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
