# EXAM-CANARY-b0de2b78 : exam gap-fill case
import json, re

case = json.load(open("case.json", encoding="utf-8"))
best = None
for page in case["web_fixture"]:
    m = re.search(r"## (\d+\.\d+\.\d+) \((\d{4}-\d{2}-\d{2})\)", page["content"])
    if m and (best is None or m.group(2) > best[1]):
        best = (m.group(1), m.group(2))
print(json.dumps({"expected_string": best[0]}))
