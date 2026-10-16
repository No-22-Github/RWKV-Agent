# DISTILL-CANARY-aa4a1598 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '436eb24679f441c3c3abf8cceccde6f7d9a4935b412528362ce408cc8dc95465', "fixture changed"
import re
def solve(files):
    c = {}
    for p, t in files.items():
        if p.endswith(".cfg"):
            tm = [l.split("=")[1] for l in t.splitlines() if l.startswith("team=")][0]
            c[tm] = c.get(tm, 0) + 1
    out = "{" + ",".join('"%s":%d' % (k, c[k]) for k in sorted(c)) + "}\n"
    return {"turns": [{"number": len(c), "items": []}], "files": {"owners/summary.json": out}, "decoys": {}}

ans = solve(case["files"])
print(json.dumps({"files": ans["files"]}, ensure_ascii=False))
