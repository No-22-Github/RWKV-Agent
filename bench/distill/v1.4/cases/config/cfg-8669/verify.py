# DISTILL-CANARY-b3676314 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['人事/薪级通知.txt']
assert files["README.md"].startswith('工资表参数，数值取自')
assert basis.startswith('2026 年 10 月起')
m = re.search('中级技工 小时工资 (\\d+) 元', basis, re.M)
val = m.group(1)
src = files['配置/工资表参数.yaml']
old = '中级技工: 38'
assert src.count(old) == 1
new = src.replace(old, '中级技工: {V}'.replace("{V}", val))
print(json.dumps({"files": {'配置/工资表参数.yaml': new}}, ensure_ascii=False))
