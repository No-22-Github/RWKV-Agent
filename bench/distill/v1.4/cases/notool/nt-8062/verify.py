# DISTILL-CANARY-b4c42c15 : distillation case
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
for k in ['18 桌', '1288 元', '10% 服务费']:
    assert k in text
ND = 2
SUF = ''
v = 18 * (1288 + 236.5) * 1.1
v = round(v, ND)
print(json.dumps({"expected_number": v}))
