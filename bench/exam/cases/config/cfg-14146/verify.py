# EXAM-CANARY-2e54dc57 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
import re
print(json.dumps({"expected_contains_all": re.findall(r"port: (\d+)", case["files"]["deploy/services.yaml"])}))
