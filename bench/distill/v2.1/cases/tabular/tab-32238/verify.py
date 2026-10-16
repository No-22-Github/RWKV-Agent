# DISTILL-CANARY-30c79cd4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '560dd5badd50d05e660d947e8056cccfabd0d107922217b51be8817879329698', "fixture changed"
import re
def solve(files):
    a = {l.split(",")[0]: int(l.split(",")[1]) for l in files["inv/system.csv"].splitlines()[1:]}
    b = {l.split(",")[0]: int(l.split(",")[1]) for l in files["inv/stocktake.csv"].splitlines()[1:]}
    d = sorted(k for k in a if a[k] != b[k])
    return {"turns": [{"number": len(d), "items": d}], "decoys": {"TR-DECOY": len(a)}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
