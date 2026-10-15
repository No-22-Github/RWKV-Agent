# EXAM-CANARY-d343219e : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
print(json.dumps({"expected_contains_any": [str(2 ** 100), "{:,}".format(2 ** 100)]}))
