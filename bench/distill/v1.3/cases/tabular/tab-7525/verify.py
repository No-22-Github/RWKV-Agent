# DISTILL-CANARY-9fb4f08a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/seat_bookings.csv"]))
seen = set()
for r in rows:
    if r["预约月份"] == "2026-09" and r["时段"] == "晚间":
        seen.add(r["会员号"])
print(json.dumps({"expected_number": len(seen)}))
