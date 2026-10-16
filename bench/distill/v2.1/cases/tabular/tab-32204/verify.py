# DISTILL-CANARY-b81413b3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e01203a86d8a7552d555484571dbb552f806b9dcd6f236bbce3676a6b92bee06', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["library/loans-2026-09.jsonl"].splitlines()]
    a = sum(i["qty"] for r in rows for i in r["items"] if i["sku"] == "BK-120")
    b = sum(i["qty"] for r in rows for i in r["items"] if i["sku"].startswith("BK-120"))
    return {"turns": [{"number": a, "items": []}], "decoys": {"TR-DECOY": b}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
