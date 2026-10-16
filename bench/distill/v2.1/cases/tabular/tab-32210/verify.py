# DISTILL-CANARY-96dca928 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c6ad76b9749fa3c914b6c641b4f497bcd3ec9eef5cc39ef2b41bfe4dca2bd295', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["门店/orders-0915.jsonl"].splitlines()]
    a = sum(i["qty"] for r in rows for i in r["items"] if i["name"] == "拿铁")
    b = sum(i["qty"] for r in rows for i in r["items"] if i["name"] == "冰拿铁")
    c = sum(i["qty"] for r in rows for i in r["items"] if "拿铁" in i["name"])
    return {"turns": [{"number": a, "items": []}, {"number": b, "items": []}], "decoys": {"TR-DECOY": c}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
