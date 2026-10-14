# DISTILL-CANARY-03b46cd7 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a56fa3f840031236fae94dd085a13b93419a162e3233e3246a9ea442ea03e452', "fixture changed"
print(json.dumps({"expected_number": sum(1 for x in case["files"]["logs/app.log"].splitlines() if "[ERROR]" in x)}))
