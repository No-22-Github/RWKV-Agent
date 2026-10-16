# DISTILL-CANARY-7c3ef1dc : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '138021397fbe9bd4b1a78dce4a1a6bc719d24da2998c6962775dff3e692fe77b', "fixture changed"
import re
m = re.search('S300,显示器,(\\d+)', case["files"]['data/prices.csv'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
