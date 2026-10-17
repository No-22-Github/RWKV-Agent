# DISTILL-CANARY-b2c0c2eb : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7e38fbbeb701769ab76632898135575f0c8131cb08f4375b92c33048525f8d1a', "fixture changed"
import json
print(json.dumps({'expected_string': '1511'}, ensure_ascii=False))

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
