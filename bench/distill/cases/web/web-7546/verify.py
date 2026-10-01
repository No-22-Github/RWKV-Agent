# DISTILL-CANARY-fabf984f : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "thornreachboats.example" in e.get("url", ""))
m = re.search(r"(\d+) pound security deposit", page["content"])
print(json.dumps({"expected_number": float(m.group(1))}))
