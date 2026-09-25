# DISTILL-CANARY-dde3975e : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

paths = sorted(path for path in case["files"] if path.startswith("intake/"))
contents = [case["files"][path] for path in paths]
twins = [content for content in set(contents) if contents.count(content) > 1]

loads = "UNKNOWN"
if len(twins) == 1:
    lines = [line for line in twins[0].splitlines() if " tonnes" in line]
    loads = len(set(lines))
print(json.dumps({"expected_number": loads}))
