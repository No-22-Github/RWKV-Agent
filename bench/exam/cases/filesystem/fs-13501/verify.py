# EXAM-CANARY-a3f10c52 : exam gap-fill case
import json,re
case=json.load(open("case.json",encoding="utf-8"))
t=case["files"]["reports/q3-summary.md"]
print(json.dumps({"expected_number":float(re.search(r"营收：([\d.]+)",t).group(1))}))
