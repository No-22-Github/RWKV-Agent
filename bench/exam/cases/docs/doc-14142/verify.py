# EXAM-CANARY-38f6fb59 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
import re
v = re.findall(r"## v(\d+\.\d+\.\d+)", case["files"]["docs/release-notes.md"])[0]
print(json.dumps({"expected_contains_any": ["v" + v, v]}))
