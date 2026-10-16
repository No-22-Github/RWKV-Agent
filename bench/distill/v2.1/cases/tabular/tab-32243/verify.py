# DISTILL-CANARY-c050e7e4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5e36c274af164fa12c9eb5eb9ebe051b1e316c68d2f1604406c63268c2b6fc41', "fixture changed"
import re
def solve(files):
    rows = [json.loads(l) for l in files["orders/day.jsonl"].splitlines()]
    t = {}
    for r in rows:
        if r["amount"] is not None:
            t[r["status"]] = t.get(r["status"], 0) + r["amount"]
    out = "status,total\n" + "".join("%s,%d\n" % (k, t[k]) for k in sorted(t))
    return {"turns": [{"number": len(t), "items": []}], "files": {"orders/summary.csv": out}, "decoys": {}}

ans = solve(case["files"])
print(json.dumps({"files": ans["files"]}, ensure_ascii=False))
