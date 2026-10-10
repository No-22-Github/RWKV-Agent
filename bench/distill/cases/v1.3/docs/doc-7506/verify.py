# DISTILL-CANARY-41f8d2a9 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import csv
import io
rows = list(csv.DictReader(io.StringIO(files["policies/refund-windows.csv"])))
facts = []
for row in rows:
    if row["tier"] == "Premium annual":
        facts = [row["window_days"], row["refund_to"], row["exceptions"]]
print(json.dumps({"expected_contains_any": facts}))
