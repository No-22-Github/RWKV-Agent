# DISTILL-CANARY-7a6605d3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '898c5ad9695763d2d725a3783daa9aefa6e325674357099c0c8d7891fdc2cfb3', "fixture changed"
import re
m = re.search('rnd,(\\d+)', case["files"]['budget/2026.csv'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
