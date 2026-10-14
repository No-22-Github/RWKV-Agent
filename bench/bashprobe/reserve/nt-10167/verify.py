# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ba86be85df1a828177415ccc5c8570e127b40685ae7b2bc584b5dd220f23297d', "fixture changed"
print(json.dumps({"expected_contains_any": ["tail -f", "tail -F", "-n 100 -f", "-100f", "tail -n 100 -F"]}, ensure_ascii=False))
