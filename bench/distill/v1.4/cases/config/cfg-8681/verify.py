# DISTILL-CANARY-d27396de : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['release/NOTES-2026-09.md']
assert files["README.md"].startswith('Compose fi')
assert basis.startswith('# September ')
m = re.search('deployed to production on [\\d-]+: gateway:([\\d.]+)\\n', basis, re.M)
val = m.group(1)
src = files['deploy/compose.yaml']
old = 'registry.local/gateway:3.8.1'
assert src.count(old) == 1
new = src.replace(old, 'registry.local/gateway:{V}'.replace("{V}", val))
print(json.dumps({"files": {'deploy/compose.yaml': new}}, ensure_ascii=False))
