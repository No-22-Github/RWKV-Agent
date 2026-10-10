# DISTILL-CANARY-889a3d67 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["store/supplies.csv"]))
row = next(r for r in rows if r["item"] == "A4 复印纸")
print(json.dumps({"expected_number": int(row["sheets_per_pack"]) * int(row["packs"])}))
