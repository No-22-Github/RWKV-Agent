# DISTILL-CANARY-8af0f5da : distillation case
import json
import re

case = json.load(open("case.json"))
assert not case["files"]
p = case["turns"][1]["prompt"]
sessions = [int(x) for x in re.findall(r"(\d+)-session", p)]
rates = [int(x) for x in re.findall(r"(\d+)\s*dollars per session", p)]
assert len(sessions) == 2 and len(rates) == 2, (sessions, rates)
ask = ["which two", "Which two", "which packages", "which ones", "Which packages", "Which ones", "package names", "the two packages"]
print(json.dumps({"expected_number": sum(s * r for s, r in zip(sessions, rates)),
                  "expected_contains_any": ask}, ensure_ascii=False))
