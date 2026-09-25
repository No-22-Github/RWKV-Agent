# DISTILL-CANARY-a49b341c : distillation case
import json
import re

with open("case.json") as handle:
    case = json.load(handle)

sheets = sorted(path for path in case["files"] if path.startswith("declarations/"))
contents = [case["files"][path] for path in sheets]
twins = [content for content in set(contents) if contents.count(content) > 1]

crates = "UNKNOWN"
if len(twins) == 1:
    match = re.search(r"^Crates:\s*([0-9.]+)", twins[0], re.M)
    if match:
        crates = float(match.group(1))

print(json.dumps({"expected_number": crates}))
