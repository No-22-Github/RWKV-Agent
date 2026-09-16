# WORKBANK-CANARY-2b8f60d3 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
files = case["files"]

MONTHS = {name: i + 1 for i, name in enumerate([
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"])}

circ = files["policy/vendor-circular-31.md"]
dm = re.search(r"issued (\d{1,2}) ([A-Z][a-z]+) (\d{4})", circ.splitlines()[0])
if not dm:
    raise SystemExit("circular 31 issue date not found in title")
iso = "%04d-%02d-%02d" % (int(dm.group(3)), MONTHS[dm.group(2)], int(dm.group(1)))

items = []
for line in circ.splitlines():
    m = re.match(r"\d+\.\s+(.*)", line.strip())
    if m:
        items.append("- " + m.group(1))

for line in files["vendor-review-minutes-2026-08-19.md"].splitlines():
    s = line.strip()
    if s.startswith("Agreed:"):
        items.append("- " + s[len("Agreed:"):].strip())

checklist = "\n".join(["# Vendor onboarding checklist - " + iso, ""] + items) + "\n"
print(json.dumps({"files": {"ops/checklist.md": checklist}}))
