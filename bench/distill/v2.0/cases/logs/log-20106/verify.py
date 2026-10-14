# DISTILL-CANARY-01a149d6 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '57352bc41677d57d9b639ba5c9fbb909f1c25d8b504da54f91f91255998c349b', "fixture changed"
print(json.dumps({"expected_number": sum(1 for x in case["files"]["access.log"].splitlines() if x.endswith(" 500"))}))
