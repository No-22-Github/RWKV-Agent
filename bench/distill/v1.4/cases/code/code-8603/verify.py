# DISTILL-CANARY-b6f89ff1 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['CHANGELOG.md']
assert files["README.md"].startswith('客户端默认值。\n')
assert basis.startswith('# 版本说明\n\n## v')
m = re.search('重试上限默认值调整为 (\\d+) 次', basis, re.M)
val = m.group(1)
src = files['pkg/client/defaults.go']
old = 'MaxRetries    = 3 //'
assert src.count(old) == 1
new = src.replace(old, 'MaxRetries    = {V} //'.replace("{V}", val))
print(json.dumps({"files": {'pkg/client/defaults.go': new}}, ensure_ascii=False))
