# DISTILL-CANARY-481e0b96 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["stock/silo-card-2026-09.csv"])))
if len(rows) < 3:
    raise SystemExit("the silo card must hold a month of weekly readings")
opening = int(rows[0]["silo_1_sacks"])
closing = int(rows[-1]["silo_1_sacks"])
if opening <= closing:
    raise SystemExit("silo 1 must fall over the month")
fall = opening - closing
if fall in {opening, closing, int(rows[1]["silo_1_sacks"])}:
    raise SystemExit("the fall must not be one of the readings on the card")
print(json.dumps({"expected_number": fall}))
