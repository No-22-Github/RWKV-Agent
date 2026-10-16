# DISTILL-CANARY-7cfdd89a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6f0c16a9d28f5788e6571c354a956f665a495d1620dcc586ac20add9c4cdd9b9', "fixture changed"
import re
m = re.search('周末值班：(Dara)', case["files"]['ops/rotation-2026-09.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
