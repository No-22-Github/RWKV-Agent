# DISTILL-CANARY-21b10fac : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "status.pennanchor.example" in e.get("url", ""))
match = re.search(r"retired on (\d{4}-\d{2}-\d{2})", page["content"])
print(json.dumps({"expected_string": match.group(1)}))
