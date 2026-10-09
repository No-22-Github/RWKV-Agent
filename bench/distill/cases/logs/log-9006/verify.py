# DISTILL-CANARY-f707d329 : distillation case
import json, re
case = json.load(open("case.json"))
ids = set()
rows = case["files"]["traces/edge.log"].splitlines()
declared = int(case["files"]["traces/NOTES.txt"].split(", ")[1].split(" lines")[0])
assert len(rows) == declared, (len(rows), declared)
for row in rows:
    m = re.fullmatch(r"ts=\S+ request_id=(req-[a-z]{3}) route=/v2/quote status=(\d+) retry=(none|short|long)", row)
    assert m, row
    if m.group(2) == "429":
        ids.add(m.group(1))
print(json.dumps({"expected_number": len(ids)}))
