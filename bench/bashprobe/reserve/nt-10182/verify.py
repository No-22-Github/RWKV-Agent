# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'fb4212ec8b549c4f50d9ecf2fcb302a69d964567d2b42612f0f12d77033498ca', "fixture changed"
prompt = case["turns"][0]["prompt"]
want = ["结算"]
assert all(w in prompt for w in want)
print(json.dumps({"expected_contains_any": want}, ensure_ascii=False))
