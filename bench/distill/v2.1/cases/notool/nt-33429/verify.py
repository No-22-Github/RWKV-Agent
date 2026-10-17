# DISTILL-CANARY-f33c550f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '717277ae4626e71bf8b062ac0ab23ad827fd64e1c60ff96769438d6139af4af5', "fixture changed"
import json
print(json.dumps({'expected_string': 'QA-4471'}, ensure_ascii=False))
assert 'QA-4471' in json.dumps(case['files'], ensure_ascii=False)

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
