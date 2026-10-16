# DISTILL-CANARY-709742b3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9371ef7d5194b77513b23497ec8b1ca122c83900999273b2d39ea154e72331c7', "fixture changed"
import re
m = re.search('A-10,(\\d+)', case["files"]['inventory/stock.csv'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
