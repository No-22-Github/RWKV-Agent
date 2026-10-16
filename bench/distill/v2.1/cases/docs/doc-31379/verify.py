# DISTILL-CANARY-b45fe9a8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f4cd09828fbc77d41371588ff6057520a2209dd90357b5384994858b7a91a82b', "fixture changed"
import re
m = re.search('超过 (\\d+) 元需 CEO', case["files"]['finance/approval.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
