# DISTILL-CANARY-dc0a1b62 : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for path in f:
    if "signin" in path:
        for line in f[path].splitlines():
            assert re.match(r"^2026-10-0[67] \d\d:\d\d:\d\d user=[a-z.]+ room=[ABC] result=(OK|FAILED)$", line), line
assert "BrightPath Tutoring Center" in f["README.md"]
prompt = case["turns"][1]["prompt"]
chosen = [p for p in f if p.endswith(".log") and p in prompt]
assert len(chosen) == 1, chosen
n = sum(1 for line in f[chosen[0]].splitlines() if "result=FAILED" in line)
ask = ["which log", "which file", "which one", "which date", "Which log", "Which file", "log file path"]
print(json.dumps({"expected_number": n, "expected_contains_any": ask}, ensure_ascii=False))
