# DISTILL-CANARY-e11f8ea6 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["会议纪要/README.md"].startswith("# 会议纪要")
total = 0
count = 0
for path, text in case["files"].items():
    if path.endswith("README.md"):
        continue
    count += 1
    assert text.startswith("# 2026-"), path
    total += sum(1 for row in text.splitlines() if row.startswith("- [ ] @张三 "))
assert count == 18
print(json.dumps({"expected_number": total}))
