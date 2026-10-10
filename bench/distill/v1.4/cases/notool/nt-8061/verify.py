# DISTILL-CANARY-f59e436e : distillation case
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
for k in ['4,200 copies', '$3.47', '$412.50']:
    assert k in text
ND = 2
SUF = ''
v = 4200 * 3.47 + 4200 * 0.18 + 640 + 412.50
v = round(v, ND)
print(json.dumps({"expected_number": v}))
