# DISTILL-CANARY-0610c496 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'aa6a832dbbfcb76ff0397df2d2679b17587ffafcec04936b38fb2c048ff50f9f', "fixture changed"
import json
print(json.dumps({'expected_string': '14'}, ensure_ascii=False))

assert all(any(s in p or s in t for p, t in case['files'].items()) for s in case['turns'][0]['expect']['output_contains'])
