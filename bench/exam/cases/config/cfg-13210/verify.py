# EXAM-CANARY-728f5e2b : exam gap-fill case
import json, re
case = json.load(open("case.json", encoding="utf-8"))
n = int(re.search(r"^DB_POOL_SIZE=(\d+)", case["files"]["deploy/prod.env"], re.M).group(1))
print(json.dumps({"expected_number": n * 3}))
