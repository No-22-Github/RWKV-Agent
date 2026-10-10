# DISTILL-CANARY-e98c2a69 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["orders/september-2026.csv"])))
brindle = {r["order_id"] for r in rows
           if r["customer"] == "Brindle & Co" and r["order_date"].startswith("2026-09")}
hartwell = {r["order_id"] for r in rows
            if r["customer"] == "Hartwell Bros" and r["order_date"].startswith("2026-09")}
t1 = len(brindle)
t2 = len(hartwell)
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
