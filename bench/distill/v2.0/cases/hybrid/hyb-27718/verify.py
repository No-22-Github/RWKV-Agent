# DISTILL-CANARY-43f7d81a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["support/calls-2026-09.csv"])))
sg = 0
for r in rows:
    hour = int(r["opened_utc"][11:13])
    if 1 <= hour <= 9:
        sg += 1
out = {
    "expected_number": len(rows),
    "expected_turn_2": sg,
}
print(json.dumps(out))
