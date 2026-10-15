# EXAM-CANARY-1ae2bf0c : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
import csv, io
tot = {}
for row in csv.DictReader(io.StringIO(case["files"]["finance/expenses.csv"])):
    if "2026-07" <= row["date"][:7] <= "2026-09":
        tot[row["category"]] = tot.get(row["category"], 0) + float(row["amount"].replace("$", "").replace(",", ""))
best = max(tot, key=tot.get)
print(json.dumps({"expected_number": round(tot[best], 2)}))
