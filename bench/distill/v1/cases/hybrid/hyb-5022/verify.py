# DISTILL-CANARY-b3a8e15d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["orders/lowthorpe-2026-09.csv"])))
totals = {}
for row in rows:
    shop = row["shop"]
    totals[shop] = totals.get(shop, 0) + int(row["units"]) * float(row["unit_price"])
named = [shop for shop in totals if shop.startswith("Lowthorpe Stores")]
if len(named) != 2:
    raise SystemExit("the order file must carry two shops trading as Lowthorpe Stores")
answer = round(totals["Lowthorpe Stores (Ely)"], 2)
other = round([total for shop, total in totals.items() if shop != "Lowthorpe Stores (Ely)" and shop.startswith("Lowthorpe Stores")][0], 2)
assert answer != other, "the two shops must differ so the clarification matters"
print(json.dumps({"expected_number": answer}))
