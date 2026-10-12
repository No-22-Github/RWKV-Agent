# DISTILL-CANARY-9385f3fa : distillation case
import json
case = json.load(open("case.json"))
rows = case["files"]["var/edge-events.log"].splitlines()
assert str(len(rows)) in case["files"]["var/NOTES.txt"]
n = 0
for row in rows:
    parts = row.split(" ")
    assert len(parts) == 5 and parts[2].startswith("code="), row
    n += parts[2] == "code=E4021"
print(json.dumps({"expected_contains_any": [str(n)]}))
