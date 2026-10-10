# DISTILL-CANARY-a6744635 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['CHANGELOG.md']
assert files["README.md"].startswith('网关服务。\n')
assert basis.startswith('# 变更记录\n\n## 未')
m = re.search('## 2\\.6\\.0\\n- 网关超时由 \\d+ 秒调为 (\\d+) 秒', basis, re.M)
val = m.group(1)
src = files['src/gateway.py']
old = 'GATEWAY_TIMEOUT_S = 30'
assert src.count(old) == 1
new = src.replace(old, 'GATEWAY_TIMEOUT_S = {V}'.replace("{V}", val))
print(json.dumps({"files": {'src/gateway.py': new}}, ensure_ascii=False))
