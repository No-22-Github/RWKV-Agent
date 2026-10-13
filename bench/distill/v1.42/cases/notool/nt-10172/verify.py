# DISTILL-CANARY-9db7bc91 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '002c33e58004aa62bd1623f0f7bd4733a67784183b7b0fa9a10751105c7ce5a8', "fixture changed"
print(json.dumps({"expected_contains_any": ["grep -rn", "grep -nr", "grep -r -n", "grep -n -r", "grep -Rn", "grep -nR"]}, ensure_ascii=False))
