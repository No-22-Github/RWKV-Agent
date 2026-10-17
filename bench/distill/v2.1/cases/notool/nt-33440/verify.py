# DISTILL-CANARY-8fc9332a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd21e51b960d76daa21f71c7780b1063c2c4bccd67bb328e7d64bc2d3aa3df060', "fixture changed"
import json
print(json.dumps({'expected_string': '2026-09-09'}, ensure_ascii=False))
assert '2026-09-09' in json.dumps(case['files'], ensure_ascii=False)

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
