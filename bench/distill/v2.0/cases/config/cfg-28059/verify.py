# DISTILL-CANARY-0bc68873 : distillation case
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
for k in ['metric tonnes', 'port/crane.cfg', 'lift_capacity_lb = 88000']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["port/crane.cfg"]
v = float(re.search(r"lift_capacity_lb\s*=\s*([\d.]+)", t).group(1)) * 0.45359237 / 1000
v = round(v, ND)
print(json.dumps({"expected_number": v}))
