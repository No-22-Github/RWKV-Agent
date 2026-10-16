# DISTILL-CANARY-7bddfd98 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2522a1453c8822c510b1bec7084dfa5e629524c33458fa0b206a21394348c661', "fixture changed"
import re
m = re.search('up to (\\d+) per day', case["files"]['policies/expense.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]
assert '60' not in ans

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
