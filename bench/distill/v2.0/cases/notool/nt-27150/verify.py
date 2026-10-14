# DISTILL-CANARY-b4378908 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["ops/env_register.csv"])))
prod = [r["version"] for r in rows if r["env"] == "生产"]
if prod != ["v2"]:
    print(json.dumps({"error": "production row no longer registers v2"}))
    sys.exit(1)
print(json.dumps({"expected_string": prod[0]}))
