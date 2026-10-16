# DISTILL-CANARY-8e471a4f : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '000d097bbbb0d4370d95ea0bf57fe3c5c0281f92c586235b9e6299fc131353b0', "fixture changed"
ans = sum(1 for l in files['orders.csv'].splitlines()[1:] if l.split(',')[1] == 'BJ')
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
