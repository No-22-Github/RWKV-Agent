# DISTILL-CANARY-f5ba06b2 : distillation case
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
for k in ['7.2 小时', '粮仓/通风.yaml', '# 3 号仓通风']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["粮仓/通风.yaml"]
n = int(re.search(r"fan_count:\s*(\d+)", t).group(1))
f = float(re.search(r"flow_m3_per_h:\s*([\d.]+)", t).group(1))
v = n * f * 7.2 / 10000
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
