# DISTILL-CANARY-9481ff06 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "thornreachwharf.example" in e.get("url", ""))
m = re.search(r"adults (\d+(?:\.\d+)?) pounds", page["content"])
print(json.dumps({"expected_number": float(m.group(1))}))
