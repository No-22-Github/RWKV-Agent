# DISTILL-CANARY-62793609 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

logs = {path: len(content.encode("utf-8")) for path, content in case["files"].items()
        if path.startswith("drying/")}
fullest = max(sorted(logs), key=lambda path: logs[path])
print(json.dumps({"expected_number": logs[fullest]}))
