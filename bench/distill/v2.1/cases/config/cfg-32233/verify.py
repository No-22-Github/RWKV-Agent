# DISTILL-CANARY-342cf64b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ee4411214c14d302d8cebf1a949b6f19658469e3cddfd62997b479aeeb7a99af', "fixture changed"
import re
def solve(files):
    cs = [json.loads(t) for t in files.values()]
    a = [c for c in cs if c.get("retry", {}).get("max", 0) > 3]
    b = [c for c in cs if "retry" in c]
    return {"turns": [{"number": len(a), "items": []}], "decoys": {"TR-MISSING": len(b), "TR-TRUNC": 50}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
