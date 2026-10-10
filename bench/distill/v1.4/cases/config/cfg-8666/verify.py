# DISTILL-CANARY-5d80c910 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['变更/药房冷柜工单.txt']
assert files["README.md"].startswith('药房冷链配置。\n')
assert basis.startswith('工单 BG-301 设备')
m = re.search('设备: 冷柜A 告警上限: (\\d+) 状态: 已审批', basis, re.M)
val = m.group(1)
src = files['配置/冷柜告警.ini']
old = '告警上限 = 9  ; 单位 ℃'
assert src.count(old) == 1
new = src.replace(old, '告警上限 = {V}  ; 单位 ℃'.replace("{V}", val))
print(json.dumps({"files": {'配置/冷柜告警.ini': new}}, ensure_ascii=False))
