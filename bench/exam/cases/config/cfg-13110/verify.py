# EXAM-CANARY-9005b3ae : exam gap-fill case
import json, re

case = json.load(open("case.json", encoding="utf-8"))
m = re.search(r"^worker_concurrency:\s*(\d+)", case["files"]["config/queue.yaml"], re.M)
print(json.dumps({"expected_number": int(m.group(1))}))
