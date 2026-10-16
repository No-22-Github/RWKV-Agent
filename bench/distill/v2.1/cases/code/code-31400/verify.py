# DISTILL-CANARY-0bb44aed : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '77786377128c51e38d1fe592dd14c9ace2819a75147d832a1d9d9ee256ade1a2', "fixture changed"
import re
m = re.search('VIP_DISCOUNT = (0\\.\\d+)', case["files"]['lib/pricing.py'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
