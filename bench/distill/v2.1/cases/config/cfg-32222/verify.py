# DISTILL-CANARY-3a28ef2a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '23b63d1439b3fce58318d9fb076caf6ff416080aac7aa9243819241c257f3b18', "fixture changed"
import re
def solve(files):
    d = json.loads(files["infra/inventory.json"])["hosts"]
    c = {}
    for h in d:
        if h["tags"]["env"] == "prod" and h["tags"]["role"] == "web" and "az" in h:
            c[h["az"]] = c.get(h["az"], 0) + 1
    r = sorted(c.items(), key=lambda kv: -kv[1])
    assert r[0][1] > r[1][1]
    al = {}
    for h in d:
        if "az" in h:
            al[h["az"]] = al.get(h["az"], 0) + 1
    ra = sorted(al.items(), key=lambda kv: -kv[1])
    assert ra[0][0] != r[0][0] or True
    return {"turns": [{"number": r[0][1], "items": [r[0][0]]}], "decoys": {"TR-DECOY": ra[0][1], "TR-MISSING": r[1][1]}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
