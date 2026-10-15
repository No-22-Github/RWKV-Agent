# EXAM-CANARY-222c73a9 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
import math
n = int(next(l for l in case["files"]["event/panel.md"].splitlines() if "位嘉宾" in l).split("共")[1].split("位")[0])
print(json.dumps({"expected_contains_any": [str(math.factorial(n)), "{:,}".format(math.factorial(n))]}))
