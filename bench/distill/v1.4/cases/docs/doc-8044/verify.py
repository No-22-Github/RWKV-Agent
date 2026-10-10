# DISTILL-CANARY-304516e6 : distillation case
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
for k in ['482,600 kWh', '2026', '# PPA summary']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["ppa/summary.md"]
p = float(re.search(r"\$([\d.]+) per MWh", t).group(1))
e = float(re.search(r"([\d.]+)% per year", t).group(1))
v = p * (1 + e / 100) ** 2 * 482600 / 1000
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
