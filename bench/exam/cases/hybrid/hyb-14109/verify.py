# EXAM-CANARY-6cd45d95 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
import re
text = case["files"]["release/notes.md"]
target = "2026-09-09"  # today is Wed 2026-09-16, so last Wednesday is 7 days back
block = text.split("## " + target)[1].split("##")[0]
print(json.dumps({"expected_contains_any": [re.search(r"v\d+\.\d+\.\d+", block).group(0), re.search(r"v(\d+\.\d+\.\d+)", block).group(1)]}))
