# DISTILL-CANARY-717e4d1e : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['runbook/workers.md']
assert files["README.md"].startswith('Production')
assert basis.startswith('# Worker siz')
m = re.search('## production \\(effective 2026-10-01\\)\\nworkers: (\\d+)', basis, re.M)
val = m.group(1)
src = files['config/prod.env']
old = 'WORKERS=12'
assert src.count(old) == 1
new = src.replace(old, 'WORKERS={V}'.replace("{V}", val))
print(json.dumps({"files": {'config/prod.env': new}}, ensure_ascii=False))
