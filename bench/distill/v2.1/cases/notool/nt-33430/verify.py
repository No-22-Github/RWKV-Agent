# DISTILL-CANARY-753fec18 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd794449f3642943689f4f881a0751ea7a0ce6c030c29879310b996e726e1ef7b', "fixture changed"
import json
print(json.dumps({'expected_string': '千分位'}, ensure_ascii=False))
assert '千分位' in json.dumps(case['files'], ensure_ascii=False)

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
