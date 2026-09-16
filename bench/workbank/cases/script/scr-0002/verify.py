import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.DictReader(io.StringIO(case["files"]["wave_61.csv"])))
priority = sorted(
    (r for r in rows if r["priority"] == "yes"),
    key=lambda r: r["order_id"],
)
rest = sorted(
    (r for r in rows if r["priority"] != "yes"),
    key=lambda r: (r["carrier_service"], r["order_id"]),
)
lines = ["order_id,carrier_service,units,priority"]
for r in priority + rest:
    lines.append(",".join([r["order_id"], r["carrier_service"], r["units"], r["priority"]]))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
