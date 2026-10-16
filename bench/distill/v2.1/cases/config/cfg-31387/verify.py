# DISTILL-CANARY-b84ef395 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4f5d4568b9f0cf7f7fa323eb19702fcbe4311c8ca861305c3f822161554c2f13', "fixture changed"
import re
m = re.search('SESSION_MINUTES=(\\d+)', case["files"]['env/production.env'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
