# DISTILL-CANARY-b047b632 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ba2359c47bd6c572ebd2daa5a4c28b30def4b7886f22c409dfa3d316763349d5', "fixture changed"
import re
m = re.search('due (\\d+) days', case["files"]['vendor/terms.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
