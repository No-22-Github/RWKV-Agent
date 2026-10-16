# DISTILL-CANARY-2b0e4561 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '47d485f45a1c65e5c86baa3951f819c8bc45018791c809882a157eb59a17b23d', "fixture changed"
import re
def solve(files):
    a = {l.split(",")[0].lower() for l in files["crm/members.csv"].splitlines()[1:]}
    b = {l.split(",")[0].lower() for l in files["crm/newsletter.csv"].splitlines()[1:]}
    o = sorted(a - b)
    raw_b = {l.split(",")[0] for l in files["crm/newsletter.csv"].splitlines()[1:]}
    raw_a = {l.split(",")[0] for l in files["crm/members.csv"].splitlines()[1:]}
    return {"turns": [{"number": len(o), "items": o}], "decoys": {"TR-DECOY": len(raw_a - raw_b), "TR-NUMFMT": len(b - a)}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
