# DISTILL-CANARY-b248b8af : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['requirements.lock']
assert files["README.md"].startswith('Intake ser')
assert basis.startswith('pydantic==2.')
m = re.search('^pydantic==([\\d.]+)$', basis, re.M)
val = m.group(1)
src = files['pyproject.toml']
old = 'pydantic==2.5.3'
assert src.count(old) == 1
new = src.replace(old, 'pydantic=={V}'.replace("{V}", val))
print(json.dumps({"files": {'pyproject.toml': new}}, ensure_ascii=False))
