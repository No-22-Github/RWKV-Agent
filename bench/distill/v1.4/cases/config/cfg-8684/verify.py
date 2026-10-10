# DISTILL-CANARY-c32350d3 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['audit/findings-2026-09.txt']
assert files["README.md"].startswith('Scheduled ')
assert basis.startswith('F-12 job nig')
m = re.search('job nightly-backup: run at ([\\d:]+) ', basis, re.M)
val = m.group(1)
src = files['ops/jobs.yaml']
old = '- job: nightly-backup\n  at: "01:00"'
assert src.count(old) == 1
new = src.replace(old, '- job: nightly-backup\n  at: "{V}"'.replace("{V}", val))
print(json.dumps({"files": {'ops/jobs.yaml': new}}, ensure_ascii=False))
