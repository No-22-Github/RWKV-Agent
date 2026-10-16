# DISTILL-CANARY-e68e24ce : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '09686ec9be0e875819c5dffeae5b6e9011f9202886dd8a1a035c2b446d5f3110', "fixture changed"
import re
def solve(files):
    o = {l.split(",")[0]: int(l.split(",")[1]) for l in files["sales/orders.csv"].splitlines()[1:]}
    s = {json.loads(l)["order"]: json.loads(l)["billed"] for l in files["sales/shipments.jsonl"].splitlines()}
    diff = sorted(k for k in o if k in s and o[k] != s[k])
    only = sorted(set(s) - set(o))
    return {"turns": [{"number": len(diff), "items": diff}, {"number": len(only), "items": only}], "decoys": {"TR-DECOY": len(diff) + len(only)}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
