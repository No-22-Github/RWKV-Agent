# DISTILL-CANARY-7cf02025 : distillation case
import json


def first_nonempty(text):
    for line in text.splitlines():
        if line.strip():
            return line
    return ""


case = json.load(open("case.json", encoding="utf-8"))
count = 0
for path in sorted(case["files"]):
    if path.endswith(".txt") and (path.startswith("导出/") or path.startswith("补传/")):
        if first_nonempty(case["files"][path]).startswith("类型：台账"):
            count += 1
print(json.dumps({"expected_number": count}))
