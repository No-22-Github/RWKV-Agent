# DISTILL-CANARY-e3a85f6b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1dd0d7d2d0657fddaf38942064c3922c1ee0c0bf45e1f88387ab0646f71eaac7', "fixture changed"
import re
def solve(files):
    d = json.loads(files["mono/manifest.json"])["packages"]
    a = [k for k, v in d.items() if "lodash" in v["dependencies"]]
    b = [k for k, v in d.items() if any(x.startswith("lodash") for x in v["dependencies"])]
    return {"turns": [{"number": len(a), "items": []}], "decoys": {"TR-DECOY": len(b)}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
