# DISTILL-CANARY-4222e916 : p13-holdout eval case (eval-only, never training data)
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/outbound-2026-09.csv"])))
dates = [row["出库日期"].strip() for row in rows]
if not dates or max(dates) >= "2026-10-01":
    raise SystemExit("export window moved past September; the absence expectation is void")
print(json.dumps({"expected_contains_any": ["10月", "10 月"]}))
