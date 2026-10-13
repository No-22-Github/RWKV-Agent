# DISTILL-CANARY-e8fa2593 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2a158a3da6965ce9175dcf43bfde0bb8be18a4177e01c5877206c8e16c67d749', "fixture changed"
print(json.dumps({"expected_contains_any": ["zip -r"]}, ensure_ascii=False))
