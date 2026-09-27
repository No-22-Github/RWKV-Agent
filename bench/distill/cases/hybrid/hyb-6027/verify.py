# DISTILL-CANARY-f555dabd : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["propagation/sowing-2026.csv"])))
t1 = sum(int(r["trays"]) for r in rows
         if r["variety"] == "Nigella Miss Jekyll" and r["sown_on"].startswith("2026-04"))
t2 = sum(int(r["trays"]) for r in rows
         if r["variety"] == "Calendula Orange King" and r["sown_on"].startswith("2026-04"))
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
