# DISTILL-CANARY-37fe58b4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["rates/callout-card.csv"])))
rates = {row["item"]: (int(row["weekday"]), int(row["weekend"])) for row in rows}
if "callout_fee" not in rates:
    raise SystemExit("the rate card must carry a call-out fee")
weekday, weekend = rates["callout_fee"]
assert weekday != weekend, "the two columns must differ so the clarification matters"
print(json.dumps({"expected_number": weekend}))
