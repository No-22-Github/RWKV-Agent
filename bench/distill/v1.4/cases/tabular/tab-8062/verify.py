# DISTILL-CANARY-e7413516 : distillation case
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
for k in ['EQ-07', '132.5 元', '设备,日期,开机小时']:
    assert k in text
ND = 2
SUF = ''
rows = list(csv.DictReader(io.StringIO(case["files"]["设备/开机时长.csv"])))
v = sum(float(r["开机小时"]) for r in rows if r["设备"] == "EQ-07") * 132.5
v = round(v, ND)
print(json.dumps({"expected_number": v}))
