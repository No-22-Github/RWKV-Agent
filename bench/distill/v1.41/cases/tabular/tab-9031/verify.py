# DISTILL-CANARY-717699ae : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["data/README.md"].startswith("# Library data")
rows = case["files"]["data/library.sql"].splitlines()
assert rows[0] == "-- Library loans dump, one INSERT per loan."
count = 0
for row in rows:
    if row.startswith("INSERT INTO loans VALUES ("):
        assert row.endswith(");"), row
        count += row.endswith(", 'overdue');")
print(json.dumps({"expected_number": count}))
