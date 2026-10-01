# DISTILL-CANARY-08d5f3ea : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import re
text = files["retro/sprint-42.txt"]
facts = []
for line in text.splitlines():
    m = re.match(r"(carried|blocked):?\s+(SPT-\d+).*owner (\w+)", line)
    if m:
        facts.extend([m.group(2), m.group(3)])
facts = sorted(set(facts))
print(json.dumps({"expected_contains_any": facts}))
