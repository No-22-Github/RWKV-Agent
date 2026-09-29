# DISTILL-CANARY-d3b8f019 : distillation case
import csv
import io
import json

with open("case.json") as handle:
    case = json.load(handle)

accepted = ["August 2025", "Aug 2025", "2025-08"]
rows = list(csv.DictReader(io.StringIO(case["files"]["picking_log_2026.csv"])))
earlier = [r for r in rows if r["pick_month"] == "2025-08"]
later = [r for r in rows if r["pick_month"] == "2026-08"]
if earlier:
    raise SystemExit("picking_log_2026.csv now holds August 2025 rows; the TR-ABSENT premise is broken")
if not later:
    raise SystemExit("picking_log_2026.csv lost its August 2026 rows")
print(json.dumps({"expected_contains_any": accepted}))
