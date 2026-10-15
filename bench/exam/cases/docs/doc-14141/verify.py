# EXAM-CANARY-b9b1f7d1 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
import re
line = next(l for l in case["files"]["policy/returns.md"].splitlines() if "普通商品" in l)
print(json.dumps({"expected_contains_all": [re.search(r"(\d+) 天", line).group(1)]}))
