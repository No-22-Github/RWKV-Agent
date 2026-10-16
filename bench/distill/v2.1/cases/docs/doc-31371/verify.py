# DISTILL-CANARY-e31e9678 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6498947748d803895fb8dfb4b22b04f07c43a85e5242e54b79994e2ceb58af53', "fixture changed"
import re
m = re.search('每分钟最多 (\\d+) 次请求', case["files"]['docs/api.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]
assert '100' not in ans

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
