# DISTILL-CANARY-9267c0fc : distillation case
import csv
import io
import json

with open("case.json") as handle:
    case = json.load(handle)

accepted = ["June 2025", "Jun 2025", "2025-06"]
reader = csv.DictReader(io.StringIO(case["files"]["sailings_2026.csv"]))
rows = list(reader)
_ = sum(int(r["vehicles"]) for r in rows)
earlier = [r for r in rows if r["sailing_date"].startswith("2025-06")]
later = [r for r in rows if r["sailing_date"].startswith("2026-06")]
if earlier:
    raise SystemExit("sailings_2026.csv now holds June 2025 sailings; the TR-ABSENT premise is broken")
if not later:
    raise SystemExit("sailings_2026.csv lost its June 2026 sailings")
print(json.dumps({"expected_contains_any": accepted}))
