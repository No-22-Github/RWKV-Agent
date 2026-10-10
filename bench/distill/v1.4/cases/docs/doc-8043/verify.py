# DISTILL-CANARY-327aa56c : distillation case
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
for k in ['6 天 19 小时', '只回数字', '# 超声设备租赁合同（摘要）']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["租赁/超声设备合同.md"]
d = float(re.search(r"日租金\s*([\d.]+)\s*元", t).group(1))
v = d * (6 + 19 / 24)
v = round(v, ND)
print(json.dumps({"expected_number": v}))
