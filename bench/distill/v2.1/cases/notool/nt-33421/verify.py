# DISTILL-CANARY-324655da : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1da7c68a632a4d764d3c3c90917bc69da3eb8227b8866eff666d60b8a4de51e3', "fixture changed"
import json
print(json.dumps({'expected_string': '36万'}, ensure_ascii=False))
assert '36万' in json.dumps(case['files'], ensure_ascii=False)

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
