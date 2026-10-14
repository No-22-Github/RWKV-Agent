# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '63dba6407848cb5d1b0ac82b9a9f29b40099ead6b2fd1962d1ba4e7387f15106', "fixture changed"
prompt = case["turns"][0]["prompt"]
want = ["2026-09-11"]
assert all(w in prompt for w in want)
print(json.dumps({"expected_contains_any": want}, ensure_ascii=False))
