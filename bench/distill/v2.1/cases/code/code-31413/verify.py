# DISTILL-CANARY-505074c1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '080d21d3561bac4e8f437dfb6cbca36bbb1efb974df2c3ed46429ee5e6d178c7', "fixture changed"
import re
m = re.search('default page size (100) \\(was', case["files"]['api/changelog.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
