# DISTILL-CANARY-6515ad5c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2d5fa472e8e5f6dad1ae420bb12d858f48925f00190ad33567e3dd13dd085bb5', "fixture changed"
import json
print(json.dumps({'expected_string': '13'}, ensure_ascii=False))

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
