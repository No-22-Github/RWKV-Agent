# DISTILL-CANARY-7c1e40ab : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import re
text = files["reports/duty-handover-0930.txt"]
facts = []
for line in text.splitlines():
    if not re.match(r"^\d{2}-\d{2} ", line):
        continue
    if ("待" in line or "未" in line or "挂起" in line) and "已入库" not in line:
        facts.extend(re.findall(r"[A-Z]{1,3}-\d+", line))
facts = sorted(set(facts))
print(json.dumps({"expected_contains_any": facts}))
