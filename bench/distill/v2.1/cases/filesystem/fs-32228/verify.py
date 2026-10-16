# DISTILL-CANARY-79c8f287 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f40cb21d1a7a75b94692ad27cd7dbed7b016c03c955302ed4d1fb3a0af1d33aa', "fixture changed"
import re
def solve(files):
    req = files["deploy/REQUIRED.txt"].split()
    miss = [r for r in req if r not in files]
    return {"turns": [{"number": len(miss), "items": [m.split("/")[1] for m in miss]}], "decoys": {"TR-DECOY": len(req), "TR-TRUNC": 50}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
