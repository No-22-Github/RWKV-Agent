# DISTILL-CANARY-f5b9d88b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1e731824f94e8dd16ae59e512cb06475ba4dae44a202a0e21ca458a1e13e83a6', "fixture changed"
import re
def solve(files):
    m = {l.split(": ")[1].split(":")[0] for l in files["mon/targets.yml"].splitlines()}
    c = {json.loads(l)["hostname"] for l in files["mon/cmdb.jsonl"].splitlines()}
    a, b = sorted(m - c), sorted(c - m)
    return {"turns": [{"number": len(a), "items": a}, {"number": len(b), "items": b}], "decoys": {"TR-DECOY": len(m & c)}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
