# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '33c60c5ce5b298f5aa94423c574a880602fa8f776453b25e81829fdcf2f0d9b0', "fixture changed"
prompt = case["turns"][0]["prompt"]
want = ["East"]
assert all(w in prompt for w in want)
print(json.dumps({"expected_contains_any": want}, ensure_ascii=False))
