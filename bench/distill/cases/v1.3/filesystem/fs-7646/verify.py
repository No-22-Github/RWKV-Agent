# DISTILL-CANARY-f9759b38 : distillation case
import json


def first_nonempty(text):
    for line in text.splitlines():
        if line.strip():
            return line
    return ""


case = json.load(open("case.json", encoding="utf-8"))
count = 0
for path in sorted(case["files"]):
    if path.startswith("导出/") and path.endswith(".txt") and "/" not in path[len("导出/"):]:
        if first_nonempty(case["files"][path]).startswith("类型：台账"):
            count += 1
print(json.dumps({"expected_number": count}))
