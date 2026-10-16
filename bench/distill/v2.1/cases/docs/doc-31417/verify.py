# DISTILL-CANARY-b5ff3665 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'fd8a0a0d69321041e51516b0bf1bd1b8acd69a69591a1932322f4deac58eaf27', "fixture changed"
import re
m = re.search('留存率：新增用户 (7 天后仍活跃)的比例', case["files"]['data/glossary.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
