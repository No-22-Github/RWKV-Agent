# DISTILL-CANARY-d784be8a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bb209e58e8fe6ca2272e1cf734e5700858736fe1b7b39d07e447140c80538488', "fixture changed"
import re
m = re.search('答：(12 月 19 日)', case["files"]['faq/internal.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
