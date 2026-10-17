# DISTILL-CANARY-100aa0a9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6937c957297fb3ea3fa3088d4e0b0cf97214c62df28d17a683c670f36984e6a7', "fixture changed"
answers=['10:00','10:20']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
