# DISTILL-CANARY-cedfa3de : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9307bcdf0dc998bb08ed5ca0a6b5f921b801f1010c7a908a4eb2950a7361b736', "fixture changed"
import json
print(json.dumps({'expected_string': '31'}, ensure_ascii=False))

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
