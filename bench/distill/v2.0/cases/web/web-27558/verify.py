# DISTILL-CANARY-33a33da4 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.batchwoodbaking.example/delivery" in e.get("url", ""))
match = re.search(r"orders of (\d+) pounds or more", page["content"])
print(json.dumps({"expected_number": int(match.group(1))}))
