# DISTILL-CANARY-0c7e4b96 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["movements/september-2026.csv"])))
totals = {}
for row in rows:
    totals[row["yard"]] = totals.get(row["yard"], 0) + int(row["pallets"])
named = {yard: total for yard, total in totals.items() if yard.startswith("Marchwold")}
if len(named) != 2:
    raise SystemExit("the register must carry two yards called Marchwold")
answer = totals["Marchwold (Thornwell)"]
other = [total for yard, total in named.items() if yard != "Marchwold (Thornwell)"][0]
assert answer != other, "the two Marchwold yards must differ so the clarification matters"
print(json.dumps({"expected_number": answer}))
