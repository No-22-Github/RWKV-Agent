# DISTILL-CANARY-be680d87 : distillation case
import json
import re

with open("case.json") as handle:
    case = json.load(handle)

answer = "UNKNOWN"
for path in sorted(case["files"]):
    content = case["files"][path]
    if "kiln-dried oak" in content:
        match = re.search(r"^Bay (\S+)", content, re.M)
        if match:
            answer = match.group(1)
        break

print(json.dumps({"expected_string": answer}))
