# DISTILL-CANARY-52077ee5 : distillation case
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
for k in ['18650 册', '7.5 个印张', 'waste_allowance_pct: 3.5']:
    assert k in text
ND = 0
SUF = ''
t = case["files"]["印刷/开机参数.yaml"]
w = float(re.search(r"waste_allowance_pct:\s*([\d.]+)", t).group(1))
v = 18650 * 7.5 * (1 + w / 100)
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
