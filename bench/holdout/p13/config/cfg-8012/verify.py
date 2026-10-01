# DISTILL-CANARY-8417b4d3 : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json
import sys

case = json.load(open("case.json"))
required = [
    r["配置项"].strip()
    for r in csv.DictReader(io.StringIO(case["files"]["配置基线.csv"]))
    if r["是否必填"].strip() == "是"
]
present = set()
for line in case["files"]["deploy.env"].splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    present.add(line.split("=", 1)[0].strip())
missing = sorted(k for k in required if k not in present)
if len(missing) != 1:
    sys.exit(1)
print(json.dumps({"expected_string": missing[0]}))
