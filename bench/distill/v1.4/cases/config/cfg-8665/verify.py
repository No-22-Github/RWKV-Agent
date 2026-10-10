# DISTILL-CANARY-f1b32669 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['审批/记录.txt']
assert files["README.md"].startswith('行政部采购限额配置，')
assert basis.startswith('AP-2231 | 单笔')
m = re.search('单笔上限 \\| (\\d+) \\| 已批准', basis, re.M)
val = m.group(1)
src = files['配置/采购限额.yaml']
old = '单笔上限: 5000'
assert src.count(old) == 1
new = src.replace(old, '单笔上限: {V}'.replace("{V}", val))
print(json.dumps({"files": {'配置/采购限额.yaml': new}}, ensure_ascii=False))
