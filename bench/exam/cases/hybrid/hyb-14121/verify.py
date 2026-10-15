# EXAM-CANARY-8a33687a : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
meet = case["files"]["会议/0914周会.md"]
items = [l.split("] ", 1)[1] for l in meet.splitlines() if l.startswith("- [@我]")]
todo = case["files"]["我的待办.md"] + "".join("- [ ] %s\n" % i for i in items)
print(json.dumps({"expected_number": len(items), "files": {"我的待办.md": todo}}))
