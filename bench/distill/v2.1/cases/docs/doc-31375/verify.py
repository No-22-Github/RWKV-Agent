# DISTILL-CANARY-2d771125 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '64713a5d93d648266f01befa215cccc8df08cae9467e10b8e6dd18d6e0a60bb2', "fixture changed"
import re
m = re.search('最短长度：(\\d+) 位', case["files"]['it/security.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
