# DISTILL-CANARY-e1c1bb5c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3f8b436566499f4c04051c1dca220b8e3448771361a93264832762bf0090e88b', "fixture changed"
import json
print(json.dumps({'expected_string': 'Omar Reyes'}, ensure_ascii=False))
assert 'Omar Reyes' in json.dumps(case['files'], ensure_ascii=False)

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
