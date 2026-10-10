# DISTILL-CANARY-c1985b97 : distillation case
import json
import re

with open("case.json") as handle:
    case = json.load(handle)

sheets = {path: content for path, content in case["files"].items() if path.startswith("checklists/")}
revisions = {}
for path, content in sheets.items():
    match = re.search(r"checklist - revision (\d+)", content)
    if match:
        revisions[path] = match.group(1)

current = None
for path, content in sorted(sheets.items()):
    for other, revision in revisions.items():
        if other != path and ("Supersedes revision " + revision) in content:
            current = path

frequency = "UNKNOWN"
if current is not None:
    match = re.search(r"Frequency: every (\d+) days", sheets[current])
    if match:
        frequency = int(match.group(1))

print(json.dumps({"expected_number": frequency}))
