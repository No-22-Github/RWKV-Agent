# EXAM-CANARY-256d8186 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
row = case["files"]["inventory/batch.csv"].splitlines()[1].split(",")
print(json.dumps({"expected_contains_any": [str(int(row[1]) * int(row[2])), "{:,}".format(int(row[1]) * int(row[2]))]}))
