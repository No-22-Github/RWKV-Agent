# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'da7ebb10b0110aed0091269dbdd08ad7aa75ddd7273aa3bafc9d2fe81dba0f65', "fixture changed"
print(json.dumps({"expected_contains_any": ["mv"]}, ensure_ascii=False))
