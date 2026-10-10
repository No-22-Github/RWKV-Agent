# DISTILL-CANARY-47d1e8a9 : distillation case
import json
import re

case = json.load(open("case.json"))
path = "lab/retention-note.txt"
text = case["files"][path]
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
values = sorted(set(re.findall(r"(\d+) days", pages)))
if len(values) != 1:
    raise SystemExit("the scheme's pages do not agree on the retention period")
filled = []
for line in text.split("\n"):
    if line.startswith("Water samples:"):
        line = "Water samples: keep " + values[0] + " days"
    filled.append(line)
print(json.dumps({"files": {path: "\n".join(filled).rstrip("\n")}}))
