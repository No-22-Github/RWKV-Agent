# DISTILL-CANARY-9e7ef7e4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd503bd149fe85aead5c1293f428bbb7d0bfc6ca8a48480042c22631567fa41e5', "fixture changed"
import re
m = re.search('响应时限：(\\d+) 分钟', case["files"]['ops/oncall.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
