# DISTILL-CANARY-fb315358 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3241df22273d67e38ec4dd24b85dbd1666dc7a2044ff9a67c53fdeedc0306545', "fixture changed"
import re
m = re.search('调到 (\\d+)', case["files"]['ops/changes.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
