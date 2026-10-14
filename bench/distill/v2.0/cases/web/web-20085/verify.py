# DISTILL-CANARY-dd816fc1 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7bc34af0ec2dbeec7b989322915970183776a4651faa5826b024c2ac910f59d5', "fixture changed"
print(json.dumps({"snapshot": 1}))
