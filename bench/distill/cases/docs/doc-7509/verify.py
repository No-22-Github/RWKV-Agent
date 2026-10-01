# DISTILL-CANARY-c2a9417f : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import csv
import io
import re
letter = files["inbox/letter-0904.txt"]
order_id = re.search(r"SO-\d+", letter).group(0)
rows = list(csv.DictReader(io.StringIO(files["inbox/orders.csv"])))
facts = [order_id]
for row in rows:
    if row["order_id"] == order_id:
        facts.append(row["signed_date"])
        facts.append(row["items"])
facts = sorted(set(facts))
print(json.dumps({"expected_contains_any": facts}))
