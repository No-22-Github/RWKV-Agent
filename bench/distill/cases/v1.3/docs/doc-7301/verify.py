# DISTILL-CANARY-4a9d72e6 : distillation case
import json
import re

case = json.load(open("case.json"))
minutes = case["files"]["minutes/standup-2026-09-24.txt"]
items = re.findall(r"^- ([A-Za-z]+):.*\bdue (\d{4}-\d{2}-\d{2})", minutes, re.M)
lines = [f"- {owner}: (due {due})" for owner, due in items]
print(json.dumps({"files": {"followups/2026-09-24.md": "\n".join(lines) + "\n"}}))
