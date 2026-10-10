# DISTILL-CANARY-2b09f400 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['合同/补充协议汇总.md']
assert files["README.md"].startswith('铺面租金配置，数值来')
assert basis.startswith('# 补充协议汇总\n\n- ')
m = re.search('盖章生效）：月租 (\\d+) 元', basis, re.M)
val = m.group(1)
src = files['配置/铺面租金.yaml']
old = '月租: 16000'
assert src.count(old) == 1
new = src.replace(old, '月租: {V}'.replace("{V}", val))
print(json.dumps({"files": {'配置/铺面租金.yaml': new}}, ensure_ascii=False))
