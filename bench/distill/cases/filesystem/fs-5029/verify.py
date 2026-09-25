# DISTILL-CANARY-fa53a513 : distillation case
import json
import re

with open("case.json") as handle:
    case = json.load(handle)

paths = sorted(path for path in case["files"] if path.startswith("round-sheets/"))
contents = [case["files"][path] for path in paths]
twins = [content for content in set(contents) if contents.count(content) > 1]

drawn = "UNKNOWN"
if len(twins) == 1:
    match = re.search(r"^Drawn:\s*([0-9]+)", twins[0], re.M)
    if match:
        drawn = float(match.group(1))
print(json.dumps({"expected_number": drawn}))
