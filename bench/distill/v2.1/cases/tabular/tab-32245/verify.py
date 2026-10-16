# DISTILL-CANARY-8da0a80b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5847454560210db9938856daad50839d28118ad62f84290bae855453457cbad5', "fixture changed"
import re
def solve(files):
    c = {}
    for l in files["埋点/log.jsonl"].splitlines():
        r = json.loads(l)
        if r["event"] == "purchase":
            c[r["user"]] = c.get(r["user"], 0) + 1
    u = sorted(k for k, v in c.items() if v >= 4)
    assert len(u) >= 4
    return {"turns": [{"number": len(u), "items": []}], "files": {"埋点/heavy_users.txt": "".join(x + "\n" for x in u)}, "decoys": {}}

ans = solve(case["files"])
print(json.dumps({"files": ans["files"]}, ensure_ascii=False))
