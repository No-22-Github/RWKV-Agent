# DISTILL-CANARY-d88fb9c5 : distillation case
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
for k in ['3 令纸', '只回数字', '# 正文纸规格']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["印务/纸张规格.md"]
w = float(re.search(r"(\d+)\s*×\s*(\d+)\s*mm", t).group(1))
h = float(re.search(r"(\d+)\s*×\s*(\d+)\s*mm", t).group(2))
g = float(re.search(r"(\d+)\s*g/㎡", t).group(1))
n = int(re.search(r"每令\s*(\d+)\s*张", t).group(1))
v = 3 * n * (w / 1000) * (h / 1000) * g / 1000
v = round(v, ND)
print(json.dumps({"expected_number": v}))
