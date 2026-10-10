# DISTILL-CANARY-5565611c : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['CHANGELOG.md']
assert files["README.md"].startswith('Protocol p')
assert basis.startswith('# Changelog\n')
m = re.search('## 1\\.9\\.0 - [\\d-]+\\n- Wire protocol is now v(\\d+)', basis, re.M)
val = m.group(1)
src = files['internal/proto/version.go']
old = 'const WireVersion = 2'
assert src.count(old) == 1
new = src.replace(old, 'const WireVersion = {V}'.replace("{V}", val))
print(json.dumps({"files": {'internal/proto/version.go': new}}, ensure_ascii=False))
