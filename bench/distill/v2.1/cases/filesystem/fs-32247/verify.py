# DISTILL-CANARY-2ea25ad1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a6b4b08ec78b6c1731135e912373910bf269ae78f6b769135914cf410c86f279', "fixture changed"
import re
def solve(files):
    c = {}
    for p in files:
        if p.endswith(".dat"):
            d = p.split("/")[1]
            c[d] = c.get(d, 0) + 1
    top = max(c.items(), key=lambda kv: kv[1])
    out = "".join("%s %d\n" % (d, c[d]) for d in sorted(c))
    return {"turns": [{"number": top[1], "items": [top[0]]}, {"number": len(c), "items": []}], "files": {"资料/counts.txt": out}, "decoys": {"TR-TRUNC": 50}}

ans = solve(case["files"])
print(json.dumps({"files": ans["files"]}, ensure_ascii=False))
