# DISTILL-CANARY-93b2a5df : distillation case
import json
import re

with open("case.json") as handle:
    case = json.load(handle)

listed = [match.group(1) for match in re.finditer(r"^(DI-[0-9]+)\s+-", case["files"]["inspection-index.txt"], re.M)]
held = {path.rsplit("/", 1)[-1][:-4] for path in case["files"] if path.startswith("sheets/")}
missing = [ref for ref in listed if ref not in held]
print(json.dumps({"expected_string": missing[0] if missing else "UNKNOWN"}))
