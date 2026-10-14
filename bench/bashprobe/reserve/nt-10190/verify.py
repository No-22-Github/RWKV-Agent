# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2f03589d5753d6b0be209c06500ec1190b56424be0f99e38eb9c6f1762dd917c', "fixture changed"
prompt = case["turns"][0]["prompt"]
want = ["4"]
assert all(w in prompt for w in want)
print(json.dumps({"expected_contains_any": want}, ensure_ascii=False))
