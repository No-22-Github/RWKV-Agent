import json
import re

case = json.load(open("case.json"))
policy = case["files"]["policy/expense-policy.md"]

head = policy.splitlines()[0]
if not re.match(r"# Expense policy \(revision \d+, approved \d{1,2} [A-Z][a-z]+ \d{4}\)", head):
    raise SystemExit("expense policy header not found")

answer = "UNKNOWN"
for block in policy.split("## ")[1:]:
    title, _, body = block.partition("\n")
    text = (title + " " + body).lower()
    if any(word in text for word in ("internet", "broadband", "connectivity")):
        m = re.search(r"EUR ([0-9.,]+) per month", body)
        answer = "EUR %s per month" % m.group(1) if m else "UNKNOWN"
        break

print(json.dumps({"expected": answer}))
