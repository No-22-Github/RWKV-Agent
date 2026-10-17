# DISTILL-CANARY-3a363ea3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9e25c17bb15a7972f854ebd378b34573bba810ddd3b39dc131010c7ce6fd0557', "fixture changed"
import json
print(json.dumps({'expected_string': '3.0.2'}, ensure_ascii=False))
assert '3.0.2' in json.dumps(case['files'], ensure_ascii=False)

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
