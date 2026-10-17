# DISTILL-CANARY-817d8fab : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e525f72a855cc1677f8653867c8d43c7abe69d25b6609c4b20e1222142f93ebc', "fixture changed"
import json
print(json.dumps({'expected_string': 'leiwang@mkt.corp.example'}, ensure_ascii=False))
assert 'leiwang@mkt.corp.example' in json.dumps(case['files'], ensure_ascii=False)

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
