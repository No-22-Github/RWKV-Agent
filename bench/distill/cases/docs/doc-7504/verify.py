# DISTILL-CANARY-d94b17c6 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import csv
import io
rows = list(csv.DictReader(io.StringIO(files["faq/tickets-0912.csv"])))
facts = []
for row in rows:
    if row["macro"] == "escalate":
        facts.append(row["ticket_id"])
counts = {}
for row in rows:
    counts[row["topic"]] = counts.get(row["topic"], 0) + 1
facts.append(max(counts, key=lambda t: (counts[t], t)))
for row in rows:
    if row["topic"] == "device swap":
        facts.append(row["macro"])
facts = sorted(set(facts))
print(json.dumps({"expected_contains_any": facts}))
