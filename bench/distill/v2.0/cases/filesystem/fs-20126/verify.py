# DISTILL-CANARY-90e4dbb9 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '14acf0ec6315ac66706a69bd91b32e5478d64000696af30fa68bbe25cf584601', "fixture changed"
print(json.dumps({"expected_string": [p for p, t in case["files"].items() if "99.9%" in t][0].split("/")[-1]}, ensure_ascii=False))
