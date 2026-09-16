# WORKBANK-CANARY-7c2e91af : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
minutes = case["files"]["Minutes-2026-06-08-hr-operations.md"]

MONTHS = {name: i + 1 for i, name in enumerate([
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"])}

title = minutes.splitlines()[0]
m = re.search(r"(\d{1,2}) ([A-Z][a-z]+) (\d{4})", title)
if not m:
    raise SystemExit("meeting date not found in minutes title")
iso = "%04d-%02d-%02d" % (int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)))

body = minutes.split("Action items", 1)[1]
items = []
for line in body.splitlines():
    line = line.strip()
    if line.startswith("- "):
        items.append("- " + line[2:])

todo = "\n".join(["# Open action items - " + iso, ""] + items) + "\n"
print(json.dumps({"files": {"tasks/todo.md": todo}}))
