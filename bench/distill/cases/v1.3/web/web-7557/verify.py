# DISTILL-CANARY-914d8c24 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.cobblemere.example/visitor-info" in e.get("url", ""))
match = re.search(r"lap pool is kept at (\d+(?:\.\d+)?) degrees", page["content"])
value = float(match.group(1))
print(json.dumps({"expected_number": int(value) if value == int(value) else value}))
