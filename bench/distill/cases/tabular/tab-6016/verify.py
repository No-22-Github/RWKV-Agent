# DISTILL-CANARY-f8e61659 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["weighbridge_2026-06.csv"])))
count = sum(1 for r in rows
            if r["direction"] == "OUT" and r["material"] == "Crushed rock"
            and "2026-06-15" <= r["ticket_date"] <= "2026-06-21")
print(json.dumps({"expected_number": count}))
