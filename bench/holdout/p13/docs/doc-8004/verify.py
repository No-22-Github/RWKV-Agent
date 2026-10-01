# DISTILL-CANARY-e5814a7c : p13 holdout (eval-only)
import json
import re

MONTHS = {"January": "01", "February": "02", "March": "03", "April": "04",
          "May": "05", "June": "06", "July": "07", "August": "08",
          "September": "09", "October": "10", "November": "11", "December": "12"}


def due(text):
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if m:
        return m.group(0)
    m = re.search(r"\b([A-Z][a-z]+) (\d{1,2})\b", text)
    if m:
        return "2026-%s-%02d" % (MONTHS[m.group(1)], int(m.group(2)))
    m = re.search(r"\b(\d{1,2}) ([A-Z][a-z]+)\b", text)
    if m:
        return "2026-%s-%02d" % (MONTHS[m.group(2)], int(m.group(1)))
    raise ValueError("no date in " + text)


case = json.load(open("case.json", encoding="utf-8"))
minutes = case["files"]["minutes/staff-2026-09-24.md"]
lines = []
for item in re.findall(r"^\d+\. (.+)$", minutes, re.M):
    owner, rest = item.split(":", 1)
    m = re.search(r"\b(?:by|before|on) (.+?)\.?$", rest)
    lines.append("- %s:%s (due %s)" % (owner.strip(), rest[:m.start()].rstrip(), due(m.group(1))))
content = "\n".join(lines) + "\n"
print(json.dumps({"files": {
    "actions/2026-09-actions.md": content,
    "minutes/staff-2026-09-24.md": minutes,
    "actions/2026-08-actions.md": case["files"]["actions/2026-08-actions.md"],
}}))
