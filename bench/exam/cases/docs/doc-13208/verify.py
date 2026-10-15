# EXAM-CANARY-6c1da82c : exam gap-fill case
import json, re
case = json.load(open("case.json", encoding="utf-8"))
m = re.search(r"\| Domestic \| \$(\d+) \|", case["files"]["docs/travel-policy.md"])
print(json.dumps({"expected_number": int(m.group(1)) * 4}))
