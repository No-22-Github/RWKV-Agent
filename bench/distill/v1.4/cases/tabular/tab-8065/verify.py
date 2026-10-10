# DISTILL-CANARY-909cce7f : distillation case
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
for k in ['hardcover', 'README', 'title,format,copies,list_price', '# Q3 royalty basis']:
    assert k in text
ND = 2
SUF = ''
rows = list(csv.DictReader(io.StringIO(case["files"]["sales/q3.csv"])))
v = sum(int(r["copies"]) * float(r["list_price"]) for r in rows if r["format"] == "hardcover") * 0.55 * 0.12
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
