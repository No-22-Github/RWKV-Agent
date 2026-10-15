# EXAM-CANARY-c796df81 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
prod = case["files"]["envs/production.env"]
val = next(l.split("=")[1] for l in prod.splitlines() if l.startswith("REQUEST_TIMEOUT_SEC="))
stg = case["files"]["envs/staging.env"]
old = next(l.split("=")[1] for l in stg.splitlines() if l.startswith("REQUEST_TIMEOUT_SEC="))
print(json.dumps({"expected_contains_any": [old], "files": {"envs/staging.env": stg.replace("REQUEST_TIMEOUT_SEC=" + old, "REQUEST_TIMEOUT_SEC=" + val)}}))
