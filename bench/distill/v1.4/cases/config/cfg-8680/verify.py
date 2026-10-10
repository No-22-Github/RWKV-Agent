# DISTILL-CANARY-e1e318d1 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['maintenance/freezer-visits.log']
assert files["README.md"].startswith('Freezer co')
assert basis.startswith('2026-03-02 v')
m = re.search('2026-09-05 visit: set point (-\\d+) C', basis, re.M)
val = m.group(1)
src = files['config/freezer-3.toml']
old = 'setpoint_c = -20'
assert src.count(old) == 1
new = src.replace(old, 'setpoint_c = {V}'.replace("{V}", val))
print(json.dumps({"files": {'config/freezer-3.toml': new}}, ensure_ascii=False))
