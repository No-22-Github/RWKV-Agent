# DISTILL-CANARY-d5c8fbfe : distillation case
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
for k in ['solar/array.yaml', 'kW', 'plant: ridge-2']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["solar/array.yaml"]
pairs = re.findall(r"panels:\s*(\d+),\s*watts:\s*(\d+)", t)
v = sum(int(a) * int(b) for a, b in pairs) / 1000
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
