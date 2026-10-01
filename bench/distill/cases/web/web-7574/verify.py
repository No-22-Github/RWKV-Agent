# DISTILL-CANARY-7863c555 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.pellbridge.example/docs/v2-migration" in e.get("url", ""))
match = re.search(r"sunset is extended to (\d{4}-\d{2}-\d{2})", page["content"])
print(json.dumps({"expected_string": match.group(1)}))
