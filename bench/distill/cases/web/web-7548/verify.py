# DISTILL-CANARY-50bcc96b : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "steam-errors" in e.get("url", ""))
row = next(l for l in page["content"].splitlines() if l.startswith("- E-11"))
cells = [c.strip() for c in row.split("|")]
cause = cells[1].split(None, 1)[1]
action = cells[2].split(None, 1)[1]
phrases = []
for item in (cause, action):
    phrases.append(item)
    phrases.append(item[0].upper() + item[1:])
print(json.dumps({"expected_contains_any": phrases}))
