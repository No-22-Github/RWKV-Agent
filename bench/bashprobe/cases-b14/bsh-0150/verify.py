# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '67cdbc860d849e2e6dac383dac4f05702db6f61569e25eff84f47f4d5a9f9ec6', "fixture changed"
prompt = case["turns"][0]["prompt"]
want = ["read_users"]
assert all(w in prompt for w in want)
print(json.dumps({"expected_contains_any": want}, ensure_ascii=False))
