# DISTILL-CANARY-777fa766 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 191
assert case["files"]["值班/本周.md"].splitlines()[4] == "- 周三：孙岩"
assert case["files"]["周报/README.md"].startswith("# 周报说明")
n = 0
for path, text in case["files"].items():
    if path.startswith("周报/2026-W"):
        n += sum(1 for r in text.splitlines() if r.endswith("| 状态：延期"))
print(json.dumps({"expected_number": n}))
