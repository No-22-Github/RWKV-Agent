# DISTILL-CANARY-2af6c8e0 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import re
text = files["meeting/minutes-0402.txt"]
facts = []
for line in text.splitlines():
    if line.startswith("行动项"):
        facts.extend(re.findall(r"A-\d+", line))
facts = sorted(set(facts))
print(json.dumps({"expected_contains_any": facts}))
