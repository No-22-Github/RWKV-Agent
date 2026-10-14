# DISTILL-CANARY-a5160861 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6ba2f32c4442a2eba81ceb46dfdb32cdeff8ff6fdf1ea6d98f59cc719ad8599d', "fixture changed"
print(json.dumps({"expected_number": len(case["files"]["data/ids.txt"].splitlines())}))
