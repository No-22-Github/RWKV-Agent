# DISTILL-CANARY-fe714867 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["runs/last.txt"]
rows = [line.split() for line in text.splitlines() if line.split()]
passed = [row for row in rows if len(row) == 3 and row[1] == "passed"]
print(json.dumps({"expected_number": len(passed)}))
