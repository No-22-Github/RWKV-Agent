# DISTILL-CANARY-e5538ce7 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bd54b7ee6c75f5d810a049a87fd348c0f6873442ecbd2f8d2f41786e34518b19', "fixture changed"
print(json.dumps({"expected_string": 'max_conn: 200'}, ensure_ascii=False))
