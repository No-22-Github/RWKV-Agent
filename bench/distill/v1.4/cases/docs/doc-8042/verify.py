# DISTILL-CANARY-53210030 : distillation case
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
for k in ['140 pallets', '23 days', '# Warehouse terms']:
    assert k in text
ND = 2
SUF = ''
t = case["files"]["contracts/warehouse-terms.md"]
r = float(re.search(r"\$([\d.]+) per pallet per day", t).group(1))
fr = int(re.search(r"first (\d+) days", t).group(1))
v = 140 * (23 - fr) * r
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
