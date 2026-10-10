# DISTILL-CANARY-c5ac84ce : distillation case
import csv
import io
import json

import re
from decimal import Decimal

def parse(s, UT):
    s = s.strip()
    if s[0] == "\u00a5":
        s = s[1:] + "\u5143"
    elif s[0] == "$":
        s = s[1:] + " USD"
    m = re.match(r"^([0-9][0-9,]*(?:\.[0-9]+)?)\s*(.*)$", s)
    return Decimal(m.group(1).replace(",", "")) * UT[m.group(2).strip()]

def plain(d):
    return format(d.normalize(), "f")

def comma(s):
    a, _, b = s.partition(".")
    return "{:,}".format(int(a)) + ("." + b if b else "")

def forms(s, names):
    out = set([s, comma(s)]) if len(s.replace(".", "")) >= 4 else set()
    for nm in names:
        for v in (s, comma(s)):
            if nm in ("$", "\u00a5"):
                out.add(nm + v)
            else:
                out.add(v + " " + nm)
                out.add(v + nm)
    return sorted(out)

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]['jobs/runtimes.csv'])))
VAL, CAT, TGT, UT, ASKF, NAMES, OP = 'runtime', 'queue', 'nightly', {'ms': 1, 's': 1000}, 1000, ['秒', 's', 'seconds'], 'max'
sel = [parse(r[VAL], UT) for r in rows if TGT is None or r[CAT] == TGT]
res = (sum(sel) if OP == "sum" else max(sel)) / ASKF
print(json.dumps({"expected_contains_any": forms(plain(res), NAMES)}))
