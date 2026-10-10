# DISTILL-CANARY-f8d6c624 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.fenstanton.example/support/c2-sync-notice" in e.get("url", ""))
match = re.search(r"set for (\d{4}-\d{2}-\d{2})", page["content"])
print(json.dumps({"expected_string": match.group(1)}))
