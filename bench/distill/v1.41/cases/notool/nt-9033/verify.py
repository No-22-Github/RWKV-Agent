# DISTILL-CANARY-69991eda : distillation case
import json
case = json.load(open("case.json"))
assert len(case["files"]) == 3
for path, text in case["files"].items():
    day = path[-5]
    rows = text.splitlines()
    assert len(rows) == 3 and rows[0] == '10.0.' + day + '.1 - - "GET /index" 200', path
print(json.dumps({"expected_contains_any": ["uniq -c", "sort -rn", "sort -nr"]}))
