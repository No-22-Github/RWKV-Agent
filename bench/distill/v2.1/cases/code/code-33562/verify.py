# DISTILL-CANARY-ba1be676 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6bb66cb461ad1198856d24abaabd4f4008bddc65311a45d5e9a00a89cdef4d87', "fixture changed"
ans = 'coupon.test.js'
assert ' FAIL  src/coupon.test.js' in files['logs/jest.out']

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
