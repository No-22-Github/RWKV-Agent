# DISTILL-CANARY-c16f4bae : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '580c86860ca9be8d9603a656b438e6d26321a63b08abe4a12e237757929a6736', "fixture changed"
import re
def solve(files):
    r = {l.split(",")[0] for l in files["hr/roster.csv"].splitlines()[1:]}
    p = {l.split(",")[0] for l in files["hr/payroll-sep.csv"].splitlines()[1:]}
    o = sorted(p - r)
    return {"turns": [{"number": len(o), "items": o}], "decoys": {"TR-DECOY": len(r - p)}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
