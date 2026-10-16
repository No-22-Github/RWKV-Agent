# DISTILL-CANARY-bb956ceb : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3e64197ad9fe75d25f6e19ec6570a37e1c0a4e4efe2a68fa99a5d86a509ef44b', "fixture changed"
import re
def solve(files):
    c = {}
    for p in files:
        d = p.rsplit("/", 1)[0]
        c[d] = c.get(d, 0) + 1
    r = sorted(c.items(), key=lambda kv: -kv[1])
    assert r[0][1] > r[1][1]
    pdf = len([p for p in files if p.startswith(r[0][0] + "/") and p.endswith(".pdf")])
    logs = len([p for p in files if p.startswith(r[0][0] + "/") and p.endswith(".log")])
    assert pdf != r[0][1]
    return {"turns": [{"number": r[0][1], "items": [r[0][0]]}, {"number": pdf, "items": []}], "decoys": {"TR-TRUNC": 50, "TR-DECOY": r[1][1]}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
