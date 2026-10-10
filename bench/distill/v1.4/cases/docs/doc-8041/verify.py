# DISTILL-CANARY-8bff417d : distillation case
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
for k in ['182,600 元', '加盟/合同要点.md', '# 加盟合同要点']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["加盟/合同要点.md"]
a = float(re.search(r"管理费[^\d]*([\d.]+)%", t).group(1))
b = float(re.search(r"品牌基金[^\d]*([\d.]+)%", t).group(1))
v = 182600 * (a + b) / 100
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
