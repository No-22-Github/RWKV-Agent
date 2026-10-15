# EXAM-CANARY-60a02eb4 : exam gap-fill case
import json, re
case = json.load(open("case.json", encoding="utf-8"))
lines = case["files"]["logs/backup.log"].splitlines()
assert "FAILED" in lines[0]
last = None
for ln in lines:
    m = re.match(r"\S+ (\d+):(\d+):\d+ backup nightly SUCCESS", ln)
    if m:
        last = "%d:%s" % (int(m.group(1)), m.group(2))
        break
print(json.dumps({"expected_contains_any": [last]}))
