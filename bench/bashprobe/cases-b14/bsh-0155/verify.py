# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '32e9ec06dec800fce4a7f914e0d75401c24616d0868bb5732c5e87e630815605', "fixture changed"
print(json.dumps({"expected_contains_any": ["-F,", "-F ','", "-F','", "-F \",\"", "-F\",\""]}, ensure_ascii=False))
