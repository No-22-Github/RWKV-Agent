# DISTILL-CANARY-c5021d3c : distillation case
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
for k in ['12,480 平方米', '2 台电梯', '# 物业服务合同（收费条款）']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["物业/服务合同.md"]
a = float(re.search(r"基础服务费\s*([\d.]+)\s*元", t).group(1))
g = float(re.search(r"绿化养护\s*([\d.]+)\s*元", t).group(1))
e = float(re.search(r"电梯维保\s*([\d.]+)\s*元", t).group(1))
v = 12480 * (a + g) + 2 * e
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
