# EXAM-CANARY-7be94d18 : exam gap-fill case
import json,re
case=json.load(open("case.json",encoding="utf-8"))
t=case["files"]["config/settings.yaml"]
print(json.dumps({"expected_number":int(re.search(r"port:\s*(\d+)",t).group(1))}))
