# DISTILL-CANARY-358320dd : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7e036bae061e153a96aa3958f169d8e27bd695abfda17c342a86082da9cc3570', "fixture changed"
import re
m = re.search('持续 (\\d+ 分钟)', case["files"]['incidents/2026-09-12.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
