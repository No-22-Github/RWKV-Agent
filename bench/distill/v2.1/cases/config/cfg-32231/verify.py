# DISTILL-CANARY-10cfdf27 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8218d3d10211ef63debf17973a2c85198160c7bfd341bf692281b862b86f1235', "fixture changed"
import re
def solve(files):
    def top(t):
        return {m.group(1): m.group(2) for m in re.finditer(r"^([a-z]+): (\S+)\s*$", t, re.M)}
    on = [t for t in files.values() if top(t).get("enabled") == "true"]
    b = [t for t in on if int(top(t)["replicas"]) > 3]
    loose = [t for t in files.values() if "enabled: true" in t]
    return {"turns": [{"number": len(on), "items": []}, {"number": len(b), "items": []}], "decoys": {"TR-DECOY": len(loose), "TR-TRUNC": 50}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
