# DISTILL-CANARY-e4a90c37 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["inspections/depot-book-september.csv"])))
own = [row for row in rows if row["fleet"] == "own"]
partner = [row for row in rows if row["fleet"] == "partner"]
if not own or not partner:
    raise SystemExit("the book must carry both the own fleet and the contract fleet")
if len(own) == len(rows):
    raise SystemExit("the own count must exclude the contract rows")
print(json.dumps({"expected_number": len(own)}))
