# DISTILL-CANARY-24b47af8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c7746e6303f8b0aca899c615e940a4b293efa3b2ae440e1d8d60e44eba5c80f1', "fixture changed"

import csv, io
from collections import Counter, defaultdict

def parse(text, delim):
    lines = [l for l in text.split("\n") if l.strip() != "" and not l.startswith("#")]
    rd = list(csv.reader(lines, delimiter=delim))
    head = rd[0]
    return [dict(zip(head, r)) for r in rd[1:]], head

def N(s):
    return float(s.replace(",", ""))

def forms(v, dp):
    if dp == 0:
        s = str(int(round(v)))
        out = [s]
        if abs(int(s)) >= 1000:
            out.append("{:,}".format(int(s)))
        return out
    s = "%.*f" % (dp, v)
    whole, _, frac = s.partition(".")
    out = [s]
    g = "{:,}".format(int(whole)) + "." + frac
    if "-" in whole and int(whole) == 0:
        g = "-0." + frac
    if g != s:
        out.append(g)
    t = s.rstrip("0").rstrip(".")
    if t != s:
        out.append(t)
        tg = g.rstrip("0").rstrip(".")
        if tg != t:
            out.append(tg)
    return list(dict.fromkeys(out))

text = case["files"]['财务/报销.csv']
R, head = parse(text, ',')
CALCS = ['result = sum(N(r["金额"]) for r in R if r["科目"] == "招待")']
KINDS = ['num']
DPS = [2]
OUTS = [None]

forms_all, names, outs = [], [], {}
for src, kind, dp, out in zip(CALCS, KINDS, DPS, OUTS):
    env = {"R": R, "N": N, "Counter": Counter, "defaultdict": defaultdict}
    exec(src, env)
    res = env["result"]
    if kind in ("int", "num"):
        forms_all += [x for x in forms(res, 0 if kind == "int" else dp) if x not in forms_all]
    elif kind == "names":
        names += res
    else:
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=out[1], lineterminator="\n")
        for row in res:
            w.writerow(row)
        outs[out[0]] = buf.getvalue()
if forms_all:
    print(json.dumps({"expected_contains_any": forms_all, "names": names, "files": outs}, ensure_ascii=False))
elif outs:
    print(json.dumps({"files": outs}, ensure_ascii=False))
else:
    print(json.dumps({"expected_string": names[0], "names": names}, ensure_ascii=False))
