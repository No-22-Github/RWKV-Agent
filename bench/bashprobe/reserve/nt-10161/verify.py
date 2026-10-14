# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'dfe147d4468566b1c718bb0fa7949dff96c7b05f4e0f64582fa350253b2dd118', "fixture changed"
print(json.dumps({"expected_contains_any": ["-mtime +7"]}, ensure_ascii=False))
