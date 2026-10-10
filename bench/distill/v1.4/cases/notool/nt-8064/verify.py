# DISTILL-CANARY-f517c7bd : distillation case
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
for k in ['36 支', '120 片', '每满 1500 元减 100 元']:
    assert k in text
ND = 2
SUF = ''
gross = 36 * 48.5 + 120 * 6.35 + 15 * 42.8
v = gross - (gross // 1500) * 100
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
