# DISTILL-CANARY-dc343005 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1d87cc5079c72497d0c02ed5c1ea987d65535e6b6a68f4c1e02fc2f7253d721b', "fixture changed"
import re
m = re.search('满一年 (\\d+) 天', case["files"]['hr/leave-policy.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
