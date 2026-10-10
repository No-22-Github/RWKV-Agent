# DISTILL-CANARY-11256a3e : distillation case
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
for k in ['9860 元', '休息日加班 8 小时', '# 加班费计算规定']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["人事/加班规定.md"]
d = float(re.search(r"月薪\s*÷\s*([\d.]+)\s*÷\s*8", t).group(1))
v = 9860 / d / 8 * (12 * 1.5 + 8 * 2)
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
