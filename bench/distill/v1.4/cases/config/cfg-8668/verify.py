# DISTILL-CANARY-fa9b0426 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['容量规划.csv']
assert files["README.md"].startswith('连接池配置，各服务一')
assert basis.startswith('服务,2025 连接池,')
m = re.search('库存,\\d+,(\\d+)', basis, re.M)
val = m.group(1)
src = files['conf/pools.conf']
old = '库存.pool_size = 24'
assert src.count(old) == 1
new = src.replace(old, '库存.pool_size = {V}'.replace("{V}", val))
print(json.dumps({"files": {'conf/pools.conf': new}}, ensure_ascii=False))
