# DISTILL-CANARY-62d10a6c : distillation case
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
for k in ['出差 9 天', '财务/差旅补贴.md', '# 境外差旅补贴']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["财务/差旅补贴.md"]
u = float(re.search(r"(\d+)\s*美元/天", t).group(1))
r = float(re.search(r"汇率\s*([\d.]+)", t).group(1))
v = u * (7 + 2 * 0.5) * r
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
