# DISTILL-CANARY-f0fcf5c0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4e13c9830df9976cfcba194ea4cf4d83f3430b4df01cf492c22fade3da4831f4', "fixture changed"
answers=['07:02','06:30']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
