# DISTILL-CANARY-69600bb4 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6f2dd61509a6d0020a3fab5bd16a540c1cec8ccbcba51bbafdde66bf4cf6de2e', "fixture changed"
print(json.dumps({"fixture_paths": sorted(case["files"])}, ensure_ascii=False))
