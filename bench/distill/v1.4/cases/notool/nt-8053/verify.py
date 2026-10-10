# DISTILL-CANARY-e70ea50c : distillation case
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
for k in ['3.84 万元', '4.31 万元']:
    assert k in text
ND = 1
SUF = ''
v = (4.31 - 3.84) / 3.84 * 100
v = round(v, ND)
print(json.dumps({"expected_number": v}))
