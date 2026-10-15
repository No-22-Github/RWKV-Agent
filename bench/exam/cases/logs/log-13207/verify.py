# EXAM-CANARY-fadb5ce9 : exam gap-fill case
import json, re
case = json.load(open("case.json", encoding="utf-8"))
text = case["files"]["logs/release.log"]
assert "[smoke] host=app-02 WARN release=2026.09.3" in text
for ln in text.splitlines():
    m = re.search(r"\[(\w+)\] host=(\S+) ERROR release=2026\.09\.3", ln)
    if m:
        print(json.dumps({"expected": m.group(2)}))
