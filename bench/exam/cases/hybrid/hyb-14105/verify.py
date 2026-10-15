# EXAM-CANARY-74c286b9 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
text = case["files"]["README.md"].replace("Release date: 2026-09-20", "Release date: 2026-10-08")
print(json.dumps({"files": {"README.md": text}}))
