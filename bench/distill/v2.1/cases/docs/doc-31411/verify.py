# DISTILL-CANARY-e6f34256 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e6f115d3d4831168021c5eaf7bcb2ee2fc444e4ec1bb9b2a4553eaeab281bfe3', "fixture changed"
import re
m = re.search('Pro plan: (39) per month', case["files"]['pricing/plans-2026.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]
assert '25' not in ans

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
