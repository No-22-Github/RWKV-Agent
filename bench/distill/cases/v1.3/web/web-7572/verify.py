# DISTILL-CANARY-678eb5fa : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.brindlewooddocs.example/notices/export-v1" in e.get("url", ""))
match = re.search(r"Since (\d{4}-\d{2}-\d{2}) the v1 export endpoint", page["content"])
print(json.dumps({"expected_string": match.group(1)}))
