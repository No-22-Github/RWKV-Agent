# DISTILL-CANARY-a0c4d310 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '356f09350f3a0e1ab9d064251f96a8d13fe52791ba4a60a51cf1bd38720ded23', "fixture changed"
import re
def solve(files):
    d = json.loads(files["deploy/services.json"])["services"]
    a = [s for s in d if (s["envs"].get("prod") or {}).get("flags", {}).get("canary") is True]
    b = [s for s in d if any((e.get("flags") or {}).get("canary") is True for e in s["envs"].values())]
    return {"turns": [{"number": len(a), "items": []}], "decoys": {"TR-DECOY": len(b), "TR-MISSING": len([s for s in d if "prod" in s["envs"]])}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
