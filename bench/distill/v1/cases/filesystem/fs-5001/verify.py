# DISTILL-CANARY-678dd59e : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

files = case["files"]
reference = "screening-fri.txt"
source = files[reference]
matches = sorted(path for path in files if path != reference and files[path] == source)
print(json.dumps({"expected_string": matches[0] if matches else "UNKNOWN"}))
