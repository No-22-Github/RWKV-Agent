# DISTILL-CANARY-98895593 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ea9a4ecd918d3f4ff4f6c0925faa11e39be615db1eb25bc9fbe297f1c5978d23', "fixture changed"
ans = sum(1 for l in files['orders.csv'].splitlines()[1:] if l.split(',')[2].lower() == 'refunded')
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
