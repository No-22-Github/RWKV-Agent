# DISTILL-CANARY-3c51e2fd : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["front/checkout_policy.csv"]))
hour = 14  # checkout time stated in the prompt
charge = next(r["charge"] for r in rows
              if int(r["from_hour"]) <= hour < int(r["to_hour"]))
print(json.dumps({"expected_string": charge}))
