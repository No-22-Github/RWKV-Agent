# DISTILL-CANARY-372b20cf : distillation case
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
for k in ['30 天', '冷库/化霜.ini', '[defrost]']:
    assert k in text
ND = 1
SUF = ''
t = case["files"]["冷库/化霜.ini"]
n = int(re.search(r"cycles_per_day\s*=\s*(\d+)", t).group(1))
m = int(re.search(r"minutes_per_cycle\s*=\s*(\d+)", t).group(1))
kw = float(re.search(r"heater_kw\s*=\s*([\d.]+)", t).group(1))
v = n * m * 30 / 60 * kw
v = round(v, ND)
print(json.dumps({"expected_number": v}))
