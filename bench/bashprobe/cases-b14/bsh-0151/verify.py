# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0ecdff66bfb0fa272330973e1b9d5cfd23e58183c9f1dfbf68cca161c86f674d', "fixture changed"
print(json.dumps({"expected_contains_any": ["-k3", "-k 3", "-k3,3"]}, ensure_ascii=False))
