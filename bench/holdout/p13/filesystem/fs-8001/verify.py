# DISTILL-CANARY-ced60e2d : p13-holdout eval case (eval-only, never training data)
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
if "exports/requests-2024.csv" in files:
    raise SystemExit("2024 archive present; the absence expectation is void")
rows = list(csv.DictReader(io.StringIO(files["exports/requests-2025.csv"])))
if not rows or "request_id" not in rows[0]:
    raise SystemExit("2025 export layout changed; the absence check is void")
print(json.dumps({"expected_contains_any": ["requests-2024", "requests-2025"]}))
