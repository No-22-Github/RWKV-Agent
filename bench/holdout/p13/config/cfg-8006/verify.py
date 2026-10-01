# DISTILL-CANARY-7c3f08b2 : p13 holdout (eval-only)
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.DictReader(io.StringIO(case["files"]["roster/2026Q4-openings.csv"])))
row = next(r for r in rows if r["site_id"] == "kw-2203")
if row["tier"] == "试点":
    timeout = 30
else:
    timeout = {"A": 90, "B": 60, "C": 45}[row["tier"]]
values = {
    "site_name": row["site_name"],
    "city": row["city"],
    "lockers": row["lockers"],
    "timeout_seconds": str(timeout),
    "notify_email": row["notify_email"],
}
lines = []
for line in case["files"]["config/sites/kiosk-1.ini"].splitlines():
    key = line.split("=", 1)[0].strip()
    lines.append(key + " = " + values[key])
content = "\n".join(lines) + "\n"
print(json.dumps({"files": {
    "config/sites/kw-2203.ini": content,
    "config/sites/kiosk-1.ini": case["files"]["config/sites/kiosk-1.ini"],
    "docs/网点接入清单.md": case["files"]["docs/网点接入清单.md"],
    "roster/2026Q4-openings.csv": case["files"]["roster/2026Q4-openings.csv"],
}}))
