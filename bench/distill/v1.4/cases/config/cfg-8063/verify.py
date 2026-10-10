# DISTILL-CANARY-18b0a1f5 : distillation case
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
for k in ['840 公斤', '航空/运价.yaml', '# 附加费均按基础运费计，两项相加后一并加收']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["航空/运价.yaml"]
r = float(re.search(r"base_rate_per_kg:\s*([\d.]+)", t).group(1))
f = float(re.search(r"fuel_surcharge_pct:\s*([\d.]+)", t).group(1))
k = float(re.search(r"peak_surcharge_pct:\s*([\d.]+)", t).group(1))
v = 840 * r * (1 + (f + k) / 100)
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
