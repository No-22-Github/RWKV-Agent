# DISTILL-CANARY-cdb98cb5 : distillation case
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
for k in ['North', '3.6 MJ', 'date,site,kwh']:
    assert k in text
ND = 1
SUF = ''
rows = list(csv.DictReader(io.StringIO(case["files"]["pv/daily-output.csv"])))
v = sum(float(r["kwh"]) for r in rows if r["site"] == "North") * 3.6
v = round(v, ND)
print(json.dumps({"expected_number": v}))
