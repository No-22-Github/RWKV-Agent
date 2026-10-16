# DISTILL-CANARY-22dcc640 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ff57b42f713abb849a8dbfcc7485b7253d680737f302953f705c1149d2c93551', "fixture changed"
import re
m = re.search('每 (60) 天轮换', case["files"]['security/keys.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
