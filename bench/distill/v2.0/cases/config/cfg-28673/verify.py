# DISTILL-CANARY-000dcbd1 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['公告/收费通知.txt']
assert files["README.md"].startswith('园区收费配置。\n')
assert basis.startswith('【2026-01-05】')
m = re.search('调整为 每小时 (\\d+) 元（自 2026-09-01 起）', basis, re.M)
val = m.group(1)
src = files['配置/园区收费.yaml']
old = '停车费每小时: 5'
assert src.count(old) == 1
new = src.replace(old, '停车费每小时: {V}'.replace("{V}", val))
print(json.dumps({"files": {'配置/园区收费.yaml': new}}, ensure_ascii=False))
