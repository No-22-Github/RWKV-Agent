# DISTILL-CANARY-1412132b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c96d1310b30cba7080a31ce44da6503af348df208cd7b0503f40c4ca66a77239', "fixture changed"
import json
print(json.dumps({'expected_string': '7081'}, ensure_ascii=False))

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
