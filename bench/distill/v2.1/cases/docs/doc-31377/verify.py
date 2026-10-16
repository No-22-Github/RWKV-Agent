# DISTILL-CANARY-1ac5261b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f019bfa02130d584399e988e01da31d34231f8db1893638c2182a2e940698bd6', "fixture changed"
import re
m = re.search('(周五) 10:00 发布', case["files"]['release/process.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
