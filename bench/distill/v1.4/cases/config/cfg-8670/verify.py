# DISTILL-CANARY-849f4ad5 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['package-lock.json']
assert files["README.md"].startswith('后台前端。版本以 p')
assert basis.startswith('{\n  "package')
m = re.search('node_modules/dayjs": \\{"version": "([^"]+)"', basis, re.M)
val = m.group(1)
src = files['package.json']
old = '"dayjs": "1.10.7"'
assert src.count(old) == 1
new = src.replace(old, '"dayjs": "{V}"'.replace("{V}", val))
print(json.dumps({"files": {'package.json': new}}, ensure_ascii=False))
