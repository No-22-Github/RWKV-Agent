# DISTILL-CANARY-3146aa55 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["billing/aug-sep-2026.csv"])))
def parse(s):
    return float(s.replace("$", "").replace(",", ""))
august = sum(parse(r["amount"]) for r in rows
             if r["fleet"] == "Brackley Couriers" and r["completed_on"].startswith("2026-08"))
september = sum(parse(r["amount"]) for r in rows
                if r["fleet"] == "Brackley Couriers" and r["completed_on"].startswith("2026-09"))
t1 = round(august, 2)
t2 = round(september, 2)
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
