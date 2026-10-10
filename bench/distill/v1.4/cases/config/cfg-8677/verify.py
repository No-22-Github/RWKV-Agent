# DISTILL-CANARY-38a6b12d : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['approvals/log-retention.txt']
assert files["README.md"].startswith('Retention ')
assert basis.startswith('CR-77 | log ')
m = re.search('log retention \\| (\\d+) days \\| APPROVED', basis, re.M)
val = m.group(1)
src = files['config/retention.env']
old = 'LOG_RETENTION_DAYS=90'
assert src.count(old) == 1
new = src.replace(old, 'LOG_RETENTION_DAYS={V}'.replace("{V}", val))
print(json.dumps({"files": {'config/retention.env': new}}, ensure_ascii=False))
