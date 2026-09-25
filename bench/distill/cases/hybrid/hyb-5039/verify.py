# DISTILL-CANARY-1c7be5f0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["press/presshouse-book-september.csv"])))
litres = sum(int(row["volume_l"]) for row in rows)
barrels = sum(int(row["volume_bbl"]) for row in rows)
if litres <= barrels:
    raise SystemExit("the litres column must carry the larger numbers")
print(json.dumps({"expected_number": litres}))
