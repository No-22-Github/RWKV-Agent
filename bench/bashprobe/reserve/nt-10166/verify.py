# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1bd07ce6eb585f88243e3d58f995b668cbaeedaa8ed1c24a0a795128456a2bf1', "fixture changed"
print(json.dumps({"expected_contains_any": ["sed -i"]}, ensure_ascii=False))
