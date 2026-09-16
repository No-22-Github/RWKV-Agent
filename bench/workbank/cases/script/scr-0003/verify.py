import csv
import io
import json
from datetime import date, datetime

case = json.load(open("case.json", encoding="utf-8"))
start = date(2026, 8, 10)
end = date(2026, 9, 8)
active = set()
for row in csv.DictReader(io.StringIO(case["files"]["signins.csv"])):
    if row["status"] != "success":
        continue
    day = datetime.fromisoformat(row["signed_in_at"]).date()
    if start <= day <= end:
        active.add(row["account_id"])
ids = sorted(active)
lines = [
    "weekly active workspaces: %d" % len(ids),
    "window: %s..%s" % (start.isoformat(), end.isoformat()),
]
lines += ids
print(json.dumps({"expected_stdout": "\n".join(lines)}))
