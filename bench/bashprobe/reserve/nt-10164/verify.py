# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8a3ec2bf3b2a5b0526fd5012225210261b05c59a564de7db1a6f3b2138f9ac39', "fixture changed"
print(json.dumps({"expected_contains_any": ["lsof", "ss -", "netstat"]}, ensure_ascii=False))
