# DISTILL-CANARY-842e8ab6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cd0c08156e51a442b5ab4adf1c00284065ac32fd71a671c1d6598895e2896106', "fixture changed"
import re
m = re.search('P1 incidents: first response within (\\d+) minutes', case["files"]['support/sla.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]
assert '60' not in ans

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
