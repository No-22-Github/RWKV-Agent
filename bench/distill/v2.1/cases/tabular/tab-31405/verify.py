# DISTILL-CANARY-062aedc9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8c3705e2a4dfe03255321308bbe8c66e754e8416e4004be2fcac4f34359e000d', "fixture changed"
import re
m = re.search('east,(\\d+)', case["files"]['sales/targets.csv'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
