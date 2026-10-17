# DISTILL-CANARY-21251ddd : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '095e80bf65241250f8d21f3040c4739ce004b20765ebbe6d2a586abc043801c6', "fixture changed"
import json
print(json.dumps({'expected_string': '2026-12-02'}, ensure_ascii=False))
assert '2026-12-02' in json.dumps(case['files'], ensure_ascii=False)

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
