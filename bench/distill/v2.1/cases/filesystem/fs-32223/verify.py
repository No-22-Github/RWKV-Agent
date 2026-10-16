# DISTILL-CANARY-2d1c0e5e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '47a7b3a70631afd0afe18dd3c109de05c42d6970523a25e7bc457b576ee59a5c', "fixture changed"
import re
def solve(files):
    n = [p for p in files if p.endswith(".png")]
    b = [p for p in files if ".png" in p]
    return {"turns": [{"number": len(n), "items": []}], "decoys": {"TR-DECOY": len(b), "TR-TRUNC": 50}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
