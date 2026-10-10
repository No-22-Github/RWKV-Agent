# DISTILL-CANARY-2ff773b9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["products/offering_2026.csv"]))
row = next(r for r in rows if r["product"] == "盈九月度款")
rate = float(row["annual_rate_pct"])
days = float(row["term_days"])
print(json.dumps({"expected_number": round(100000 * rate * days / 365 / 100, 2)}))
