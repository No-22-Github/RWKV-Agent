# DISTILL-CANARY-b3bdf6db : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2c382c24d58cfd5e40eb6e4523100acd0bfb560034912ae6a90ea7d3ca957564', "fixture changed"
print(json.dumps({"expected_contains_any": ["head -10", "head -n 10", "head -n10"]}, ensure_ascii=False))
