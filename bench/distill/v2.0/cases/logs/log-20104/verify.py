# DISTILL-CANARY-5da248d4 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '08636f27ecbae2f824dcab0d70e732bf23e6ac37fb818bd0f3840abf2c080cf6', "fixture changed"
ls = case["files"]["logs/gateway.log"].splitlines()
print(json.dumps({"expected_number": sum(1 for x in ls if "timeout" in x)}))
