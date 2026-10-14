# DISTILL-CANARY-c87f3a95 : distillation case
import json
import re

case = json.load(open("case.json"))
text = case["files"]["ingest/queue.py"]
match = re.search(r"(?m)^EMPTY_PAUSE_SECONDS = (\d+)$", text)
print(json.dumps({"expected_number": int(match.group(1))}))
