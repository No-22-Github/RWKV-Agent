# DISTILL-CANARY-964da8fa : distillation case
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
for k in ['9 月 8 日到 14 日', '只回数字', '日期,发电量kWh']:
    assert k in text
ND = 1
SUF = ''
rows = list(csv.DictReader(io.StringIO(case["files"]["电站/日发电量.csv"])))
a = sum(int(r["发电量kWh"]) for r in rows[:7])
b = sum(int(r["发电量kWh"]) for r in rows[7:14])
v = (b - a) / a * 100
v = round(v, ND)
print(json.dumps({"expected_number": v}))
