# DISTILL-CANARY-126d9859 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

files = case["files"]
missing = []
for line in files["accession-index.txt"].splitlines():
    if " - " not in line:
        continue
    path = line.split(" - ", 1)[1].strip()
    if path not in files:
        missing.append(path)

answer = missing[0] if len(missing) == 1 else "UNKNOWN"
print(json.dumps({"expected_string": answer}))
