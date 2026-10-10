# DISTILL-CANARY-14a32784 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["deliveries/kegs-2026.csv"])))
t1 = sum(int(r["kegs"]) for r in rows
         if r["depot"] == "Marsland Depot" and r["drop_date"].startswith("2026-06"))
t2 = sum(int(r["kegs"]) for r in rows
         if r["depot"] == "Talverne Depot" and r["drop_date"].startswith("2026-06"))
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
