# DISTILL-CANARY-3c7e05da : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "help.qingwu.example" in e.get("url", ""))
row = next(l for l in page["content"].splitlines() if l.startswith("- E-3102"))
cells = [c.strip() for c in row.split("|")]
cause = cells[1].split(None, 1)[1]
action = cells[2].split(None, 1)[1]
print(json.dumps({"expected_contains_any": [cause, action]}))
