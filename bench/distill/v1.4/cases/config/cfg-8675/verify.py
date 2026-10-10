# DISTILL-CANARY-2dfea69a : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['poetry.lock']
assert files["README.md"].startswith('Deploy ins')
assert basis.startswith('[[package]]\n')
m = re.search('name = "requests"\\nversion = "([^"]+)"', basis, re.M)
val = m.group(1)
src = files['requirements.txt']
old = 'requests==2.31.0'
assert src.count(old) == 1
new = src.replace(old, 'requests=={V}'.replace("{V}", val))
print(json.dumps({"files": {'requirements.txt': new}}, ensure_ascii=False))
