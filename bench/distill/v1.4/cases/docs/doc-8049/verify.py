# DISTILL-CANARY-fe50a279 : distillation case
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
for k in ['5 days 9 hours', 'charter/terms.md', '# Charter summary']:
    assert k in text
ND = 1
SUF = ''
t = case["files"]["charter/terms.md"]
lay = int(re.search(r"[Ll]aytime of (\d+) hours", t).group(1))
d = float(re.search(r"\$([\d,]+) per day", t).group(1).replace(",", ""))
v = (5 * 24 + 9 - lay) * d / 24
v = round(v, ND)
print(json.dumps({"expected_contains_any": [f + SUF for f in fmt(v, ND)]}))
