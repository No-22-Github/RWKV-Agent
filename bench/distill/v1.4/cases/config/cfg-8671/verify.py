# DISTILL-CANARY-b5f26011 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['会议/排班委员会纪要.md']
assert files["README.md"].startswith('门诊号源配置。\n')
assert basis.startswith('## 2026-09-1')
m = re.search('专家门诊每号时长改 (\\d+) 分钟——表决通过', basis, re.M)
val = m.group(1)
src = files['配置/号源.yaml']
old = '  每号分钟: 15   # 2026-03 起'
assert src.count(old) == 1
new = src.replace(old, '  每号分钟: {V}   # 2026-03 起'.replace("{V}", val))
print(json.dumps({"files": {'配置/号源.yaml': new}}, ensure_ascii=False))
