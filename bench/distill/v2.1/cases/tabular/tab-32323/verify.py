# DISTILL-CANARY-68d95681 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '23859d0472eefd31335992a7e8abf58ed6c6102ecf9fe402cc749ef667110a55', "fixture changed"
ans = len(files['orders_2026-09.csv'].splitlines()) - 1
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
