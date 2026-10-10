# DISTILL-CANARY-0d6e42bb : distillation case
import json

case = json.load(open("case.json"))
failed = ""
for line in case["files"]["board/lastrun.txt"].splitlines():
    if line.startswith("FAIL "):
        failed = line.split(None, 1)[1].strip()
        break
print(json.dumps({"expected_string": failed}))
