# DISTILL-CANARY-f7e7c145 : distillation case
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
for k in ['site/genset.yaml', '$1.38', 'fuel_burn_lph: 14.6']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["site/genset.yaml"]
b = float(re.search(r"fuel_burn_lph:\s*([\d.]+)", t).group(1))
h = float(re.search(r"daily_run_hours:\s*([\d.]+)", t).group(1))
v = b * h * 30 * 1.38
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
