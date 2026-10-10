# DISTILL-CANARY-f3ca9ea4 : distillation case
import json
import re

with open("case.json") as handle:
    case = json.load(handle)

notes = {path: content for path, content in case["files"].items() if path.startswith("notes/")}
contents = list(notes.values())
distinct = [path for path in sorted(notes) if contents.count(notes[path]) == 1]

weight = "UNKNOWN"
if len(distinct) == 1:
    match = re.search(r"Consignment weight:\s*([0-9.]+)", notes[distinct[0]])
    if match:
        weight = float(match.group(1))

print(json.dumps({"expected_number": weight}))
