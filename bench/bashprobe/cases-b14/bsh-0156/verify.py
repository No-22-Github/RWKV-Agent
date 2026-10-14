# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9db675da41bf27253a7b38c73d2058b6dcffb530d67b247a34ff9718d8ae4f4f', "fixture changed"
print(json.dumps({"expected_contains_any": ["sort -u", "uniq"]}, ensure_ascii=False))
