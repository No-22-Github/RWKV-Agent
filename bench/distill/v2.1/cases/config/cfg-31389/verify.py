# DISTILL-CANARY-3f928125 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '36cb4452d9e0d3dc2d46bf81d9d07ddd9a87c43de307efc1dce11ff7e5004b08', "fixture changed"
import re
m = re.search('cron: \\"(30 2 \\* \\* \\*)\\"', case["files"]['scheduler/jobs.yaml'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
