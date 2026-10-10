# DISTILL-CANARY-e0578a37 : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for path in f:
    if path.endswith(".log"):
        for line in f[path].splitlines():
            assert re.match(r"^2026-09-1[56] \d\d:\d\d:\d\d ", line), (path, line)
assert "记为告警" in f["游泳馆/日志/说明.md"]
prompt = case["turns"][1]["prompt"]
chosen = [p for p in f if p.endswith(".log") and p in prompt]
assert len(chosen) == 1, chosen
n = sum(1 for line in f[chosen[0]].splitlines() if "告警" in line)
ask = ["哪一份", "哪份", "哪个日志", "哪个文件", "文件名", "文件路径", "日志路径"]
print(json.dumps({"expected_number": n, "expected_contains_any": ask}, ensure_ascii=False))
