# EXAM-CANARY-adaccf5c : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
env = case["files"]["app/.env"]
print(json.dumps({"files": {"app/.env": env.replace("LOG_LEVEL=info", "LOG_LEVEL=debug")}}))
