# DISTILL-CANARY-bc65abd9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2f5e703742e6a5415851740d967c1b4d474fd9fe8d6f724e5a8865ab81792f8f', "fixture changed"
ans = '800'
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
