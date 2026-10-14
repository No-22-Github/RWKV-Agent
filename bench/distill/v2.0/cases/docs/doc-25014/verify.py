# DISTILL-CANARY-6e94c7b1 : distillation case
import json
import re

case = json.load(open("case.json"))
manual = case["files"]["manual/safety-manual.md"]

# The edition states the window of work it applies to.
line = next(l for l in manual.splitlines() if "applies to inspection work carried out between" in l)
print(json.dumps({"expected_number": int(re.search(r"Edition (\d+)", line).group(1))}))
