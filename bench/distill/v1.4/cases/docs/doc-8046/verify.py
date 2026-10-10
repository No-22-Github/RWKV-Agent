# DISTILL-CANARY-93269f64 : distillation case
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
for k in ['11,800 copies', '$24.95', '# Author agreement - royalties']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["contracts/author-agreement.md"]
v = (5000 * 0.10 + 5000 * 0.125 + (11800 - 10000) * 0.15) * 24.95
assert "10%" in t and "12.5%" in t and "15%" in t
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
