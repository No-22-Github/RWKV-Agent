# DISTILL-CANARY-71ea26d4 : distillation case
import csv
import io
import json

with open("case.json") as handle:
    case = json.load(handle)

accepted = ["April 2025", "Apr 2025", "2025-04"]
reader = csv.DictReader(io.StringIO(case["files"]["collection_log_2026.csv"]))
rows = list(reader)
_ = sum(int(r["litres"]) for r in rows)
earlier = [r for r in rows if r["collection_date"].startswith("2025-04")]
later = [r for r in rows if r["collection_date"].startswith("2026-04")]
if earlier:
    raise SystemExit("collection_log_2026.csv now holds April 2025 rounds; the TR-ABSENT premise is broken")
if not later:
    raise SystemExit("collection_log_2026.csv lost its April 2026 rounds")
print(json.dumps({"expected_contains_any": accepted}))
