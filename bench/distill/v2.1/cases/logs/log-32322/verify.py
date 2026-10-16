# DISTILL-CANARY-4930b192 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '15896fd8c18fc1248403c767e40ed474c6b1277b3dbdc7cfa948a90709d29cb9', "fixture changed"
ans = sum(1 for l in files['auth.log'].splitlines() if 'user:admin ' in l)
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
