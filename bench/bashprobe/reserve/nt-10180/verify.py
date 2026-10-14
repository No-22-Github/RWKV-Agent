# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2f6b2cdb8d83d9cedfba2f924584346468036de48e84dc5260b7d8bec5c359db', "fixture changed"
print(json.dumps({"expected_contains_any": ["--exclude-dir", "-not -path", "! -path", "-prune"]}, ensure_ascii=False))
