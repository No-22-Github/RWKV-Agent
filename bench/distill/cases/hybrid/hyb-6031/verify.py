# DISTILL-CANARY-7c18554f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["despatches/nov-dec-2025.csv"])))
wrekin = {r["despatch_id"] for r in rows
          if r["customer"] == "Wrekin Garden Co" and r["despatch_date"].startswith("2025-12")}
pensfold = {r["despatch_id"] for r in rows
            if r["customer"] == "Pensfold Growers" and r["despatch_date"].startswith("2025-12")}
t1 = len(wrekin)
t2 = len(pensfold)
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
