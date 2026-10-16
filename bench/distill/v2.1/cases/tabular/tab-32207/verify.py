# DISTILL-CANARY-4ef8be88 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cc85cb13bfcef2fc94b271fefb35bf01694018b84955496cfccaf4568071663d', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["support/tickets.jsonl"].splitlines()]
    a = [r for r in rows if r["priority"] == "P1" and r["resolved_at"] is not None]
    b = [r for r in a if "billing" in r["tags"]]
    p1 = [r for r in rows if r["priority"] == "P1"]
    return {"turns": [{"number": len(a), "items": []}, {"number": len(b), "items": []}], "decoys": {"TR-MISSING": len(p1), "TR-DECOY": len([r for r in p1 if "billing" in r["tags"]])}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
