# DISTILL-CANARY-44cb5344 : distillation case
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
for k in ['$482.60', 'payments/fees.toml', '[fees]']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["payments/fees.toml"]
bps = float(re.search(r"card_fee_bps\s*=\s*([\d.]+)", t).group(1))
fx = float(re.search(r"card_fixed_fee_usd\s*=\s*([\d.]+)", t).group(1))
v = 482.60 * bps / 10000 + fx
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
