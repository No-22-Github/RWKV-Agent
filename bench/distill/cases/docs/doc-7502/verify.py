# DISTILL-CANARY-59b2d3f1 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import re
text = files["docs/CHANGELOG.txt"]
lines = text.splitlines()
head = lines[0]
facts = [re.search(r"v\d+\.\d+\.\d+", head).group(0),
         re.search(r"\d{4}-\d{2}-\d{2}", head).group(0)]
for line in lines[1:]:
    if re.match(r"v\d+\.\d+\.\d+", line):
        break
    facts.extend(re.findall(r"BC-\d+", line))
facts = sorted(set(facts))
print(json.dumps({"expected_contains_any": facts}))
