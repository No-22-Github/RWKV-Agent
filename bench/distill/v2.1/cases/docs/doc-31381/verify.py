# DISTILL-CANARY-92a7ad33 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '31d7e20d8d874c92f9dbf92ed94e47f928ebc3cb4c71ca424d99d78f1ee7e6ef', "fixture changed"
import re
m = re.search('每(周三下午)为无会议时间', case["files"]['team/working-hours.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
