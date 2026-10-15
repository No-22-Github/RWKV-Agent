# EXAM-CANARY-e1330098 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
for line in case["files"]["deploy/prod.env"].splitlines():
    if line.startswith("DB_POOL_SIZE="):
        print(json.dumps({"expected_string": line.split("=", 1)[1]}))
