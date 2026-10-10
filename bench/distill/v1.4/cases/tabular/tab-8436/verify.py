# DISTILL-CANARY-4c1fb15f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
CFG = {'path': '接单/打印任务.csv', 'hdr': ['任务号', '收件日', '纸张', '页数'], 'month': 4, 'a': 1, 'b': 5, 'kind': 'catsum', 'cat': 'A4', 'zh': True, 'unit': '页'}

import re

MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def parse(s):
    """-> (month, day) of a date cell; dmy cells are day-month-year."""
    m = re.match(r"2026/(\d\d)/(\d\d)$", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r"(\d\d)-(\d\d)-2026$", s)
    if m:
        return int(m.group(2)), int(m.group(1))
    m = re.match(r"([A-Z][a-z][a-z]) (\d+), 2026$", s)
    if m:
        return MON.index(m.group(1)) + 1, int(m.group(2))
    m = re.match(r"2026-(\d\d)-(\d\d)T08:00:00Z$", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    raise AssertionError(s)

def comma(s):
    return "{:,}".format(int(s))

def forms(n, zh, unit, kind):
    """-> (mode, list) of accepted writings of the number n."""
    s = str(n)
    if kind == "count":
        if zh:
            return "any", sorted({"%d%s%s" % (n, sp, u) for u in (unit, "个", "条") for sp in (" ", "")})
        return "token", [s]
    base = sorted({s, comma(s)})
    if zh:
        return "any", sorted({b + sp + unit for b in base for sp in (" ", "")})
    return "any", base

rows = list(csv.DictReader(io.StringIO(case["files"][CFG["path"]])))
assert "README.md" in case["files"] and len(rows) >= 60
hd, hc, ha = CFG["hdr"][1], CFG["hdr"][2], CFG["hdr"][3]
assert len({r[hd] for r in rows}) <= 40
kind = CFG["kind"]
pick = [r for r in rows if CFG["a"] <= parse(r[hd])[1] <= CFG["b"] and parse(r[hd])[0] == CFG["month"] and (kind in ("count", "sum") or r[hc] == CFG["cat"])]
v = sum(int(r[ha]) for r in pick) if kind in ("sum", "catsum") else len(pick)
mode, lst = forms(v, CFG["zh"], CFG["unit"], "sum" if kind in ("sum", "catsum") else "count")
if mode == "token":
    print(json.dumps({"expected_number": float(lst[0])}))
else:
    print(json.dumps({"expected_contains_any": lst}, ensure_ascii=False))
