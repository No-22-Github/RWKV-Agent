# DISTILL-CANARY-5e08b6d1 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import csv
import io
import re
rows = list(csv.DictReader(io.StringIO(files["hr/pto-balances.csv"])))
facts = []
for row in rows:
    if int(row["days_left"]) > int(row["carryover_cap"]):
        facts.append(row["employee"])
policy = files["hr/pto-policy.md"]
facts.append(re.search(r"On (\w+ \d+)", policy).group(1))
facts = sorted(set(facts))
print(json.dumps({"expected_contains_any": facts}))
