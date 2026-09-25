# DISTILL-CANARY-6b2e9d05 : distillation case
import json
import re

case = json.load(open("case.json"))
path = "config/washer.json"
text = case["files"][path]

# The trial note states the interval the washer is run at for the trial.
note = case["files"]["docs/reclaim-trial.md"]
match = re.search(r"drain interval of (\d+) seconds", note)
if match is None:
    raise SystemExit("the trial note does not state a drain interval")

filled = []
for line in text.split("\n"):
    if line.strip().startswith('"drain_interval_s"'):
        filled.append('  "drain_interval_s": %s,' % match.group(1))
    else:
        filled.append(line)
final = "\n".join(filled).rstrip("\n")
print(json.dumps({"files": {path: final}}))
