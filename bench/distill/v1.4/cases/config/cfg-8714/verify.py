# DISTILL-CANARY-badacc75 : distillation case
import hashlib
import json

case = json.load(open("case.json"))
assert hashlib.sha256(json.dumps(case["files"], sort_keys=True, ensure_ascii=False).encode()).hexdigest().startswith('7462a92322f693f5')
print(json.dumps({"expected_contains_any": ["conflict", "disagree", "differ", "contradict", "inconsistent", "two tickets", "both tickets"]}, ensure_ascii=False))
