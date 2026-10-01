# DISTILL-CANARY-d349d8ea : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "open.nanzhi.example/notices" in e.get("url", ""))
row = next(l for l in page["content"].splitlines() if "/v1/files/upload" in l)
m = re.search(r"停用于 API 版本 (\d+)", row)
print(json.dumps({"expected_number": float(m.group(1))}))
