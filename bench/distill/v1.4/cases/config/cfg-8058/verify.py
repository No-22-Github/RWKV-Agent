# DISTILL-CANARY-d22178f2 : distillation case
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
for k in ['华氏度', '灭菌/锅炉参数.yaml', 'program: B-class']:
    assert k in text
ND = 1
SUF = ''
t = case["files"]["灭菌/锅炉参数.yaml"]
f = float(re.search(r"hold_temp_f:\s*([\d.]+)", t).group(1))
v = (f - 32) * 5 / 9
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
