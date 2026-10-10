# DISTILL-CANARY-bf171f92 : distillation case
import hashlib
import json

case = json.load(open("case.json"))
assert hashlib.sha256(json.dumps(case["files"], sort_keys=True, ensure_ascii=False).encode()).hexdigest().startswith('b5e65395c7996a0e')
print(json.dumps({"expected_contains_any": ["conflict", "disagree", "differ", "contradict", "inconsistent", "two tickets", "both tickets"]}, ensure_ascii=False))
