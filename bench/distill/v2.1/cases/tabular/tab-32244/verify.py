# DISTILL-CANARY-2ce56942 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1b7ce1f1fbcfc092943c237e721f8570174b60ae93c446a2bb990acb76233442', "fixture changed"
import re
def solve(files):
    t = {}
    for l in files["sales/week.csv"].splitlines()[1:]:
        p, u, pr = l.split(",")
        t[p] = t.get(p, 0) + int(u) * int(pr)
    r = sorted(t.items(), key=lambda kv: -kv[1])[:3]
    assert r[2][1] > sorted(t.values())[-4]
    out = "".join("%d. %s: %d\n" % (k + 1, p, v) for k, (p, v) in enumerate(r))
    return {"turns": [{"number": r[0][1], "items": [r[0][0]]}, {"number": 3, "items": []}], "files": {"report/top3.txt": out}, "decoys": {}}

ans = solve(case["files"])
print(json.dumps({"files": ans["files"]}, ensure_ascii=False))
