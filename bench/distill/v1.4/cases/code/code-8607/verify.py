# DISTILL-CANARY-3e039c11 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['CHANGELOG.md']
assert files["README.md"].startswith('Admin serv')
assert basis.startswith('# Changelog\n')
m = re.search('## 3\\.1\\.0\\n- Default admin port moves from \\d+ to (\\d+)', basis, re.M)
val = m.group(1)
src = files['src/config.ts']
old = 'ADMIN_PORT = 9000'
assert src.count(old) == 1
new = src.replace(old, 'ADMIN_PORT = {V}'.replace("{V}", val))
print(json.dumps({"files": {'src/config.ts': new}}, ensure_ascii=False))
