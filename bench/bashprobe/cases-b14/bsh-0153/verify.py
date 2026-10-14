# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '84e8b094d0a3e69338f53e7611da79d04eb74be258dd08dc16238d0413088508', "fixture changed"
prompt = case["turns"][0]["prompt"]
want = ["4500"]
assert all(w in prompt for w in want)
print(json.dumps({"expected_contains_any": want}, ensure_ascii=False))
