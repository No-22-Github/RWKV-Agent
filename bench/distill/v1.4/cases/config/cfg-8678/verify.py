# DISTILL-CANARY-dabfcada : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['reviews/cdn-2026-09.md']
assert files["README.md"].startswith('CDN rules.')
assert basis.startswith('# CDN review')
m = re.search('/static/js \\| \\d+ \\| (\\d+)', basis, re.M)
val = m.group(1)
src = files['infra/cdn.yaml']
old = '  - path: /static/js\n    ttl: 3600'
assert src.count(old) == 1
new = src.replace(old, '  - path: /static/js\n    ttl: {V}'.replace("{V}", val))
print(json.dumps({"files": {'infra/cdn.yaml': new}}, ensure_ascii=False))
