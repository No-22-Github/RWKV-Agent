# DISTILL-CANARY-b1dff566 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f58fcc496fab30deedc3f9c401a5eb6fb835e4f567b6dbb7cdd81aed9428d3d0', "fixture changed"

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

text = case["files"]['预算/执行.csv']
R, head = parse(text, ',')
CALCS = ['b = defaultdict(float); a = defaultdict(float)\nfor r in R:\n    b[r["科目"]] += N(r["预算"]); a[r["科目"]] += N(r["实际"])\nresult = [["科目", "预算合计", "实际合计", "差额"]] + [[k, "%.2f" % b[k], "%.2f" % a[k], "%.2f" % (a[k] - b[k])] for k in sorted(b)]']
KINDS = ['files']
DPS = [0]
OUTS = [('预算/科目对比.csv', ',')]

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
