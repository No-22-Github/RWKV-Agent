# DISTILL-CANARY-5de5f865 : distillation case
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
for k in ['320 件', '只回数字', 'per_piece_yuan: 0.85']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["灭菌/外包费率.yaml"]
p = float(re.search(r"per_piece_yuan:\s*([\d.]+)", t).group(1))
b = float(re.search(r"base_fee_per_batch_yuan:\s*([\d.]+)", t).group(1))
v = (320 + 450 + 275) * p + 3 * b
v = round(v, ND)
print(json.dumps({"expected_number": v}))
